msgBus.on("screen:changed", (payload, event) => {
  if (payload === "guard") {
    console.log("Guard status monitor initialized");
  }
});
