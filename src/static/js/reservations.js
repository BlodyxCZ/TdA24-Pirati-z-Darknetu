document.addEventListener("DOMContentLoaded", () => {
    const hour0 = document.getElementById("hour-0");
    for (let index = 0; index < 6; index++) {
        const element = document.createElement("div");
        element.style.flexGrow = Math.random() * 20 + 5;
        element.style.background = index % 2 ? "#0f0" : "";
        hour0.appendChild(element);
    }
});