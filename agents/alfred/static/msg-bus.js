/**
 * Simple message bus for posting messages between frames using window.postMessage.
 *
 * Usage:
 *   msgBus.post({ type: "event", payload: ... });
 *   msgBus.on("event", (payload, event) => { ... });
 *
 * AI-REQ: Defensive programming, no inheritance, clean composition.
 */

const msgBus = (() => {
  const listeners = {};

  /**
   * Register a handler for a specific message type.
   * @param {string} type - The message type to listen for.
   * @param {(payload: any, event: MessageEvent) => void} handler - Handler function.
   */
  function on(type, handler) {
    if (typeof type !== "string") throw new TypeError("type must be a string");
    if (typeof handler !== "function")
      throw new TypeError("handler must be a function");
    if (!listeners[type]) listeners[type] = [];
    listeners[type].push(handler);
  }

  /**
   * Remove a handler for a specific message type.
   * @param {string} type
   * @param {function} handler
   */
  function off(type, handler) {
    if (!listeners[type]) return;
    listeners[type] = listeners[type].filter((h) => h !== handler);
  }

  /**
   * Post a message to all frames (parent, children, self).
   * @param {object} msg - Must have a string 'type' property.
   * @param {string} [targetOrigin="*"]
   */
  function post(msg, targetOrigin = "*") {
    if (!msg || typeof msg.type !== "string")
      throw new TypeError("msg.type must be a string");
    // Post to parent if not self
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(msg, targetOrigin);
    }
    // Post to all child frames
    for (const frame of Array.from(window.frames)) {
      try {
        frame.postMessage(msg, targetOrigin);
      } catch (e) {
        // AI-REQ: Defensive - ignore cross-origin errors
      }
    }
    // Also post to self (for local listeners)
    window.postMessage(msg, targetOrigin);
  }

  // Listen for messages and dispatch to handlers
  window.addEventListener("message", (event) => {
    const { data } = event;
    if (!data || typeof data.type !== "string") return;
    const handlers = listeners[data.type] || [];
    for (const handler of handlers) {
      try {
        handler(data.payload, event);
      } catch (e) {
        // AI-REQ: Defensive - never throw from handler
        // Optionally log error
        // console.error("msgBus handler error", e);
      }
    }
  });

  return { on, off, post };
})();

window.msgBus = msgBus;
