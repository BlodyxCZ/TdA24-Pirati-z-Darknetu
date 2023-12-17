document.addEventListener("DOMContentLoaded", (e) => {
    setInterval(() => {
        update();
    }, 500);

    const logContainer = document.getElementById("log");
    logContainer.addEventListener("scroll", (e) => {
        scroll = (logContainer.scrollTop >= logContainer.scrollHeight - logContainer.offsetHeight - 10);
    });
})

var scroll = true;

function update() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            const logContainer = document.getElementById("log");
            let lines = xmlHttp.responseText.split("\n");
            if (lines.length < logContainer.children.length) {
                logContainer.innerHTML = "";
            }
            lines = lines.splice(logContainer.children.length, lines.length - logContainer.children.length - 1);
            let nodes = lines.map((l) => {
                let element = document.createElement("div");
                console.log(l);
                element.textContent = l;
                element.innerHTML = ansiToHtml(element.innerHTML);
                return element;
            });
            for (let i = 0; i < nodes.length; i++) {
                logContainer.appendChild(nodes[i]);
            }

            if (scroll) {
                logContainer.scrollTop = logContainer.scrollHeight;
                setTimeout(() => {
                    logContainer.scrollTop = logContainer.scrollHeight;
                }, 100);
            };
        }
    }
    xmlHttp.open("GET", "/api/log", true);
    xmlHttp.send(null);
}

function ansiToHtml(ansiString) {
    const ansiColors = [
        'black',
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        'white',
    ];
    let htmlString = '';
    let currentColor = '';
    let bold = false;
    let underline = false;

    ansiString.split(/(\x1b\[[0-9;]*m)/).forEach((part) => {
        if (part.startsWith('\x1b[')) {
            const codes = part.slice(2, -1).split(';');
            codes.forEach((code) => {
                if (code === '0') {
                    currentColor = '';
                    bold = false;
                    underline = false;
                } else if (code === '1') {
                    bold = true;
                } else if (code === '4') {
                    underline = true;
                } else if (code >= 30 && code <= 37) {
                    currentColor = ansiColors[code - 30];
                } else if (code >= 90 && code <= 97) {
                    currentColor = ansiColors[code - 90 + 8];
                }
            });
        } else {
            let style = '';
            if (bold) {
                style += 'font-weight: bold;';
            }
            if (underline) {
                style += 'text-decoration: underline;';
            }
            if (currentColor) {
                style += `color: ${currentColor};`;
            }
            htmlString += `<span style="${style}">${part}</span>`;
        }
    });

    return htmlString;
}
