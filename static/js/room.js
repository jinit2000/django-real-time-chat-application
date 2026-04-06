// This file handles the live chat on the room page.
(function () {
  'use strict';

  const messagesArea = document.getElementById('messages-area');
  const chatForm = document.getElementById('chat-form');
  const messageInput = document.getElementById('message-input');
  const connectionStatus = document.getElementById('connection-status');
  const statusText = connectionStatus ? connectionStatus.querySelector('.status-text') : null;
  const participantsList = document.getElementById('participants-list');

  let socket = null;
  let reconnectDelay = 1000;
  let isConnected = false;

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socketUrl = `${protocol}//${window.location.host}/ws/chat/${ROOM_ID}/`;

    setStatus('connecting');
    socket = new WebSocket(socketUrl);

    socket.onopen = function () {
      isConnected = true;
      reconnectDelay = 1000;
      setStatus('connected');
      scrollToBottom();
    };

    socket.onmessage = function (event) {
      const data = JSON.parse(event.data);
      handleMessage(data);
    };

    socket.onclose = function () {
      isConnected = false;
      setStatus('disconnected');

      setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 1.5, 10000);
        connect();
      }, reconnectDelay);
    };

    socket.onerror = function () {
      socket.close();
    };
  }

  function setStatus(state) {
    if (!connectionStatus || !statusText) return;

    connectionStatus.className = `connection-status ${state}`;

    const labels = {
      connecting: 'Connecting',
      connected: 'Connected',
      disconnected: 'Reconnecting',
    };

    statusText.textContent = labels[state] || state;
  }

  function handleMessage(data) {
    if (data.type === 'message') {
      appendMessage(data);
      scrollToBottom();
      return;
    }

    if (data.type === 'user_join') {
      appendSystemMessage(`${data.username} joined the room`);
      addParticipant(data.username, data.user_id);
      return;
    }

    if (data.type === 'user_leave') {
      appendSystemMessage(`${data.username} left the room`);
      return;
    }

    if (data.type === 'message_deleted') {
      markDeleted(data.message_id);
    }
  }

  function appendMessage(data) {
    const isSelf = data.user_id === CURRENT_USER_ID;
    const canDelete = isSelf || IS_HOST;
    const wrapper = document.createElement('div');
    const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(data.username)}&backgroundColor=dbe4ff`;

    wrapper.className = `message${isSelf ? ' message-self' : ''}`;
    wrapper.dataset.messageId = data.message_id;

    wrapper.innerHTML = `
      <a href="/profile/${data.user_id}/" class="message-avatar">
        <img src="${avatarUrl}" alt="${escapeHtml(data.username)}">
      </a>
      <div class="message-content">
        <div class="message-header">
          <a href="/profile/${data.user_id}/" class="message-username">${escapeHtml(data.username)}</a>
          <span class="message-time" title="${data.full_timestamp}">${data.timestamp}</span>
          ${canDelete ? `<button class="delete-msg-btn" data-message-id="${data.message_id}" title="Delete">×</button>` : ''}
        </div>
        <p class="message-body">${escapeHtml(data.body)}</p>
      </div>
    `;

    messagesArea.appendChild(wrapper);

    const deleteButton = wrapper.querySelector('.delete-msg-btn');
    if (deleteButton) {
      deleteButton.addEventListener('click', () => deleteMessage(data.message_id));
    }
  }

  function appendSystemMessage(text) {
    const note = document.createElement('div');
    note.className = 'system-message';
    note.textContent = text;
    messagesArea.appendChild(note);
  }

  function markDeleted(messageId) {
    const messageBox = messagesArea.querySelector(`[data-message-id="${messageId}"]`);
    if (!messageBox) return;

    const body = messageBox.querySelector('.message-body');
    const deleteButton = messageBox.querySelector('.delete-msg-btn');

    if (body) {
      body.textContent = '[deleted]';
      messageBox.classList.add('deleted');
    }

    if (deleteButton) {
      deleteButton.remove();
    }
  }

  function sendMessage() {
    const body = messageInput.value.trim();
    if (!body || !isConnected) return;

    socket.send(JSON.stringify({ type: 'message', body }));
    messageInput.value = '';
    messageInput.style.height = 'auto';
    messageInput.focus();
  }

  function deleteMessage(messageId) {
    if (!confirm('Delete this message?')) return;

    if (isConnected) {
      socket.send(JSON.stringify({ type: 'delete', message_id: messageId }));
    }

    fetch(`/message/${messageId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
    });
  }

  function addParticipant(username, userId) {
    if (!participantsList || participantsList.querySelector(`[data-user-id="${userId}"]`)) return;

    const row = document.createElement('li');
    row.className = 'participant-item';
    row.dataset.userId = userId;
    row.innerHTML = `
      <img src="https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(username)}&backgroundColor=dbe4ff" alt="${escapeHtml(username)}">
      <a href="/profile/${userId}/">${escapeHtml(username)}</a>
    `;

    participantsList.appendChild(row);
    updateCount();
  }

  function updateCount() {
    const badge = document.querySelector('.count-badge');
    if (!participantsList || !badge) return;

    badge.textContent = participantsList.querySelectorAll('.participant-item').length;
  }

  function scrollToBottom() {
    if (!messagesArea) return;
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  if (chatForm) {
    chatForm.addEventListener('submit', function (event) {
      event.preventDefault();
      sendMessage();
    });
  }

  if (messageInput) {
    messageInput.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
      }
    });

    messageInput.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = `${Math.min(this.scrollHeight, 120)}px`;
    });
  }

  document.querySelectorAll('.delete-msg-btn').forEach((button) => {
    button.addEventListener('click', function () {
      deleteMessage(Number(this.dataset.messageId));
    });
  });

  connect();
  scrollToBottom();
})();
