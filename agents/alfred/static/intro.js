msgBus.on("screen:changed", (payload, event) => {
  if (payload === "intro") {
    console.log("Intro status monitor initialized");
  }
});
