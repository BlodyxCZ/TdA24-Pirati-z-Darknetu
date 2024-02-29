const hours = [];
var reservations = [];
var today = new Date();
today.setHours(0, 0, 0, 0);
var tomorrow = clone(today) + new Date(0, 0, 1);
console.log(today, tomorrow);
var token = null;

document.addEventListener("DOMContentLoaded", () => {
    token = getCookie("token");
    const datePicker = document.getElementById("date");
    datePicker.value = today;

    datePicker.addEventListener("change", () => {
        today = new Date(datePicker.value);
        displayReservations(reservations);
    });

    const backLecturerButton = document.getElementById("back-lecturer");
    const backStudentButton = document.getElementById("back-student");

    backLecturerButton.addEventListener("click", closePopup);
    backStudentButton.addEventListener("click", closePopup);

    const submitLecturerButton = document.getElementById("submit-lecturer");
    const submitStudentButton = document.getElementById("submit-student");

    submitLecturerButton.addEventListener("click", submitLecturer);
    submitStudentButton.addEventListener("click", submitStudent);

    for (let i = 0; i < 24; i++) {
        hours.push(document.getElementById(`hour-${i}`));
    }

    loadReservations();
});

function loadReservations() {
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
}

function displayReservations(data) {
    console.log(data);

    data.sort(compareReservations);

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


                let segmentUUID = data[reservationIterator].uuid;
                let segmentEnd = new Date(data[reservationIterator].end_date);
                if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                } else {
                    reservationIterator++;
                }
                hour.appendChild(createSegment(segmentStart, segmentEnd, "#ff0", segmentUUID));
                currentTime = clone(segmentEnd);
            } else {
                let segmentEnd = reservationIterator < data.length ? new Date(data[reservationIterator].start_date) : clone(nextHour);
                if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                }
                hour.appendChild(createSegment(segmentStart, segmentEnd, "#f00", null));
                currentTime = clone(segmentEnd);
            }
        }
    }
}

function createSegment(start, end, color, uuid) {
    let diff = new Date(end.getTime() - start.getTime());
    const element = document.createElement("div");
    console.log("diff: ", diff.getUTCHours() * 60 + diff.getUTCMinutes());
    element.style.flexGrow = diff.getUTCHours() * 60 + diff.getUTCMinutes();
    element.style.background = color;
    element.style.cursor = "pointer";
    element.setAttribute("start-time", start);
    element.setAttribute("end-time", end);
    element.setAttribute("uuid", uuid);
    if (uuid == null) {
        element.addEventListener("click", openPopup);
    } else {
        element.addEventListener("click", deleteFreeTime);
    }
    return element;
}

function clone(date) {
    return new Date(date.getTime());
}

function openPopup(e) {
    document.getElementById("popup").style.display = "flex";
    if (token != null) {
        document.getElementById("lecturer-popup").style.display = "block";
        document.getElementById("student-popup").style.display = "none";

        const startTime = new Date(e.target.getAttribute("start-time"));
        const endTime = new Date(e.target.getAttribute("end-time"));

        document.getElementById("start-time").value = startTime.toTimeString().substring(0, 5);
        document.getElementById("end-time").value = endTime.toTimeString().substring(0, 5);

    } else {
        document.getElementById("lecturer-popup").style.display = "none";
        document.getElementById("student-popup").style.display = "block";
    }
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
}

function submitLecturer() {
    let startTime = document.getElementById("start-time").value;
    let endTime = document.getElementById("end-time").value;

    if (startTime == null || endTime == null) {
        return;
    }

    let startDate = clone(today);
    let endDate = clone(today);

    startDate.setHours(startTime.substring(0, 2));
    startDate.setMinutes(startTime.substring(3, 5));

    endDate.setHours(endTime.substring(0, 2));
    endDate.setMinutes(endTime.substring(3, 5));

    if (startDate.getTime() >= endDate.getTime()) {
        return;
    }

    fetch(`/api/free-times/${uuid}`, {
        method: "POST",
        headers: {
            "Authorization": `Basic ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            token: token
        })
    })
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
            loadReservations();
        });
}

function deleteFreeTime(e) {
    if (!confirm("Opravdu chcete smazat tento volný čas?")) {
        return;
    }

    fetch(`/api/free-times/${uuid}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Basic ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            uuid: e.target.getAttribute("uuid"),
            token: token
        })
    })
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
            loadReservations();
        });
}

function submitStudent() {

}

function compareReservations(a, b) {
    if (new Date(a.start_date).getTime() < new Date(b.start_date).getTime()) {
        return -1;
    } else if (new Date(a.start_date).getTime() > new Date(b.start_date).getTime()) {
        return 1;
    }
    return 0;
}