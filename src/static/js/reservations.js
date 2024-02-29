const hours = [];
var reservations = [];
var today = new Date();
today.setHours(0, 0, 0, 0);
var tomorrow = clone(today) + new Date(0, 0, 1);
console.log(today, tomorrow);

document.addEventListener("DOMContentLoaded", () => {
    const token = getCookie("token");
    const datePicker = document.getElementById("date");
    datePicker.value = today;

    datePicker.addEventListener("change", () => {
        today = new Date(datePicker.value);
        displayReservations(reservations);
    });

    for (let i = 0; i < 24; i++) {
        hours.push(document.getElementById(`hour-${i}`));
    }

    fetch(`/api/reservations/${uuid}`, {
        method: "GET",
        headers: token != null ? {
            "Authorization": `Basic ${token}`
        } : {}
    })
        .then((response) => response.json())
        .then((json) => {
            reservations = json;
            displayReservations(reservations);
        });
});

function displayReservations(data) {
    console.log(data);

    data.sort((a, b) => { new Date(b.start_date) - new Date(a.start_date) });

    console.log(data);

    let reservationIterator = 0;

    while (new Date(data[reservationIterator].end_date) <= today || new Date(data[reservationIterator].start_date) > tomorrow) {
        console.log("skipping: ", data[reservationIterator]);
        reservationIterator++;
    }

    for (let i = 0; i < hours.length; i++) {
        let currentTime = clone(today);
        currentTime.setHours(i);
        const nextHour = clone(today);
        nextHour.setHours(i + 1);

        const hour = hours[i];
        hour.innerHTML = "";

        while (currentTime.getTime() < nextHour.getTime()) {
            let segmentStart = clone(currentTime);

            if (reservationIterator < data.length &&
                currentTime.getTime() < new Date(data[reservationIterator].end_date).getTime() &&
                currentTime.getTime() >= new Date(data[reservationIterator].start_date).getTime()) {

                console.log("Rendering reservation: ", data[reservationIterator]);

                let segmentEnd = new Date(data[reservationIterator].end_date);
                if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                } else {
                    reservationIterator++;
                }
                hour.appendChild(createSegment(segmentStart, segmentEnd, "#ff0"));
                currentTime = clone(segmentEnd);
            } else {
                let segmentEnd = reservationIterator < data.length ? new Date(data[reservationIterator].start_date) : clone(nextHour);
                if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                }
                hour.appendChild(createSegment(segmentStart, segmentEnd, "#f00"));
                currentTime = clone(segmentEnd);
            }
        }
    }
}

function createSegment(start, end, color) {
    let diff = new Date(end.getTime() - start.getTime());
    const element = document.createElement("div");
    console.log("diff: ", diff.getUTCHours() * 60 + diff.getUTCMinutes());
    element.style.flexGrow = diff.getUTCHours() * 60 + diff.getUTCMinutes();
    element.style.background = color;
    return element;
}

function clone(date) {
    return new Date(date.getTime());
}