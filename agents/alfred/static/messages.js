(async () => {
  const messagesDiv = document.getElementById("messages");

  msgBus.on("status", (payload, event) => {
    onMessageCb(payload);
  });

  const onMessageCb = (data) => {
    console.log("status event:", data);
    const msg = document.createElement("div");
    msg.className = "msg";
    try {
      const parsed = JSON.parse(data);
      msg.textContent = JSON.stringify(parsed, null, 2);
    } catch {
      msg.textContent = data;
    }
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  };
})();
