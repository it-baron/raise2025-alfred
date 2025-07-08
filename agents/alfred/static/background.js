const iframe = document.getElementById("background");

const stateScreen = {
  intro: "/static/intro.html",
  guard: "/static/guard.html",
  alfred: "/static/alfred.html",
  tool: "/static/tool.html"
};

const onMessageCb = (data) => {
  console.log("background status event:", data);
  msgBus.post({ type: "status", payload: data });

  if (data.includes("screen:")) {
    const screen = data.split(":")[1];
    const trimmedScreen = screen.trim();
    if (stateScreen[trimmedScreen]) {
      console.log("change screen:", trimmedScreen);
      iframe.src = stateScreen[trimmedScreen];
      msgBus.post({ type: "screen:changed", payload: trimmedScreen });
    }
  }
};

(async () => {
  iframe.src = stateScreen.intro;

  listenSSE(onMessageCb);
})();
