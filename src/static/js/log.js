document.addEventListener("DOMContentLoaded", (e) => {
    setInterval(() => {
        update();
        console.log("update");
    }, 500);
})

function update() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            const logContainer = document.getElementById("log");
            let lines = xmlHttp.responseText.split("\n");
            if (lines.length < logContainer.children.length) {
                logContainer.innerHTML = "";
            }
            lines.splice(0, logContainer.children.length);
            let nodes = lines.map((l) => {
                let element = document.createElement("div");
                element.textContent = l;
                return element;
            });
            for (let i = 0; i < nodes.length; i++) {
                logContainer.appendChild(nodes[i]);
            }

        }
    }
    xmlHttp.open("GET", "/api/log", true);
    xmlHttp.send(null);
}