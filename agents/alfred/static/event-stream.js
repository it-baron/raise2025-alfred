const _evtSource = new EventSource("/status/stream");

export const listenSSE = (onMessageCb, onErrorCb = () => {}) => {
  _evtSource.addEventListener("status", function (event) {
    onMessageCb(event.data);
  });

  _evtSource.onerror = function (error) {
    console.error("Event source error", error);
    onErrorCb(error);
  };
};

window.listenSSE = listenSSE;
