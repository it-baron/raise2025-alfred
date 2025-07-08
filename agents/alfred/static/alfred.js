msgBus.on("screen:changed", (payload, event) => {
  if (payload === "alfred") {
    console.log("Alfred status monitor initialized");
  }
});
