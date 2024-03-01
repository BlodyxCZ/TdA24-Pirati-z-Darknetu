const hours = [];
var reservations = [];
var today = new Date();
today.setHours(0, 0, 0, 0);
var tomorrow = clone(today) + new Date(0, 0, 1);
console.log(today, tomorrow);
var token = null;

var data_cache = null;
var tags = [];
var selectedReservation = null;

const colorEmpty = "#777";
const colorFree = "#0f0";
const colorReservation = "#ff0";
const colorReservationUnconfirmed = "#f00";
const colorReservationConfirmed = "#ff0";

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        getLecturers();
        getTags();
    }, 500);

    token = getCookie("token");
    const datePicker = document.getElementById("date");
    datePicker.value = `${today.getFullYear()}-${('0' + (today.getMonth() + 1)).slice(-2)}-${('0' + today.getDate()).slice(-2)}`;

    datePicker.addEventListener("change", () => {
        today = new Date(datePicker.value);
        displayReservations(reservations);
    });

    const downloadiCalButton = document.getElementById("ical-button");

    downloadiCalButton.addEventListener("click", () => {
        console.log("Downloading iCal");
        downloadiCal(datePicker.value);
    });

    const backLecturerButton = document.getElementById("back-lecturer");
    const backStudentButton = document.getElementById("back-student");
    const backLecturerReservationButton = document.getElementById("back-lecturer-reservation");

    backLecturerButton.addEventListener("click", closePopup);
    backStudentButton.addEventListener("click", closePopup);
    backLecturerReservationButton.addEventListener("click", closePopup);

    const submitLecturerButton = document.getElementById("submit-lecturer");
    const submitStudentButton = document.getElementById("submit-student");

    submitLecturerButton.addEventListener("click", submitLecturer);
    submitStudentButton.addEventListener("click", submitStudent);

    const confirmReservationButton = document.getElementById("confirm-lecturer-reservation");
    const deleteReservationButton = document.getElementById("delete-lecturer-reservation");

    confirmReservationButton.addEventListener("click", confirmReservation);
    deleteReservationButton.addEventListener("click", deleteReservation);

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

function downloadiCal(date) {
    console.log(date);

    fetch(`/api/reservations/${uuid}/icalendar?date=${date}`, {
        method: "GET",
        headers: token != null ? {
            "Authorization": `Basic ${token}`
        } : {}
    })
        .then((response) => response.json())
        .then((json) => {
            if (json.code != 200) {
                alert("Na daný den není žádná rezevace.");
                return;
            }

            // download a file
            const blob = new Blob([json.ical], { type: 'text/calendar' });
            const blobUrl = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = blobUrl;
            link.download = `Výuka - ${json.first_name} ${json.last_name}.ics`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(blobUrl);
        });
}

function displayReservations(data) {
    console.log(data);

    data.sort(compareReservationsStart);

    console.log(data);

    let reservationIterator = 0;

    while (reservationIterator < data.length && (new Date(data[reservationIterator].end_date) <= today || new Date(data[reservationIterator].start_date) > tomorrow)) {
        console.log("skipping: ", data[reservationIterator]);
        reservationIterator++;
    }

    var ongoing = [];

    for (let i = 0; i < hours.length; i++) {
        let currentTime = clone(today);
        currentTime.setHours(i);
        const nextHour = clone(today);
        nextHour.setHours(i + 1);

        const hour = hours[i];
        hour.innerHTML = "";

        while (currentTime.getTime() < nextHour.getTime()) {
            let segmentStart = clone(currentTime);

            ongoing.sort(compareReservationsEnd);

            while (reservationIterator < data.length &&
                currentTime.getTime() < new Date(data[reservationIterator].end_date).getTime() &&
                currentTime.getTime() >= new Date(data[reservationIterator].start_date).getTime()) {

                console.log("Adding reservation to ongoing: ", data[reservationIterator]);
                ongoing.push(data[reservationIterator]);
                reservationIterator++;
                ongoing.sort(compareReservationsEnd);
            }

            if (ongoing.length > 0) {
                let segmentUUID = ongoing[0].uuid;
                let segmentEnd = new Date(ongoing[0].end_date);
                let type = ongoing[0].type;
                if (token != null && type == "reservation") {
                    if (ongoing[0].confirmed) {
                        type += "_confirmed";
                    } else {
                        type += "_unconfirmed";
                    }
                }

                if (segmentEnd.getTime() >= new Date(data[reservationIterator].start_date).getTime()) {
                    segmentEnd = new Date(data[reservationIterator].start_date);
                } else if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                } else {
                    ongoing.splice(0, 1);
                }
                let segment = createSegment(segmentStart, segmentEnd, type, segmentUUID);
                if (segment != null) hour.appendChild(segment);
                currentTime = clone(segmentEnd);
            } else {
                let segmentEnd = reservationIterator < data.length ? new Date(data[reservationIterator].start_date) : clone(nextHour);
                if (segmentEnd.getTime() > nextHour.getTime()) {
                    segmentEnd = clone(nextHour);
                }
                let segment = createSegment(segmentStart, segmentEnd, "empty", null);
                if (segment != null) hour.appendChild(segment);
                currentTime = clone(segmentEnd);
            }
        }
    }
}

function createSegment(start, end, type, uuid) {
    let diff = new Date(end.getTime() - start.getTime());

    if (diff.getUTCHours() * 60 + diff.getUTCMinutes() == 0) {
        return null;
    }

    const element = document.createElement("div");
    console.log("diff: ", diff.getUTCHours() * 60 + diff.getUTCMinutes());
    element.style.flexGrow = diff.getUTCHours() * 60 + diff.getUTCMinutes();
    let p = document.createElement("p");
    p.style.color = "black";

    switch (type) {
        case "empty":
            element.style.background = colorEmpty;
            p.textContent = "";
            break;
        case "free_time":
            element.style.background = colorFree;
            p.textContent = "Volný čas";
            break;
        case "reservation":
            element.style.background = colorReservation;
            p.textContent = "Rezervace";
            break;
        case "reservation_confirmed":
            element.style.background = colorReservationConfirmed;
            p.textContent = "Potvrzená rezervace";
            break;
        case "reservation_unconfirmed":
            element.style.background = colorReservationUnconfirmed;
            p.textContent = "Nepotvrzená rezervace";
            p.style.color = "white";
            break;
        default:
            break;
    }

    element.setAttribute("type", type)
    element.appendChild(p);
    element.setAttribute("start-time", start);
    element.setAttribute("end-time", end);
    element.setAttribute("uuid", uuid);
    if (uuid == null && token != null) {
        element.addEventListener("click", openPopup);
        element.style.cursor = "pointer";
    } else if (type == "free_time" && token != null) {
        element.addEventListener("click", deleteFreeTime);
        element.style.cursor = "pointer";
    } else if ((type == "reservation_confirmed" || type == "reservation_unconfirmed") && token != null) {
        element.addEventListener("click", function () { openPopup2(uuid) });
        element.style.cursor = "pointer";
    } else if (uuid != null && token == null) {
        element.addEventListener("click", openPopup);
        element.style.cursor = "pointer";
    }
    return element;
}

function clone(date) {
    return new Date(date.getTime());
}

function openPopup(e) {
    document.getElementById("popup").style.display = "flex";

    const startTime = new Date(e.target.getAttribute("start-time"));
    const endTime = new Date(e.target.getAttribute("end-time"));

    if (token != null) {
        document.getElementById("lecturer-popup").style.display = "block";
        document.getElementById("student-popup").style.display = "none";
        document.getElementById("lecturer-reservation-popup").style.display = "none";

        document.getElementById("start-time").value = startTime.toTimeString().substring(0, 5);
        document.getElementById("end-time").value = endTime.toTimeString().substring(0, 5);

    } else {
        document.getElementById("lecturer-popup").style.display = "none";
        document.getElementById("student-popup").style.display = "block";
        document.getElementById("lecturer-reservation-popup").style.display = "none";

        document.getElementById("reservation-start-time").value = startTime.toTimeString().substring(0, 5);
        document.getElementById("reservation-end-time").value = endTime.toTimeString().substring(0, 5);
    }
}

function getTagNameByUUID(uuid) {
    for (let tag of tags) {
        if (tag.uuid == uuid) {
            return tag.name;
        }
    }
}

function openPopup2(uuid) {

    let reservation = findInSet((p) => p.uuid == uuid, reservations);
    selectedReservation = reservation;
    console.log(reservation);

    document.getElementById("popup").style.display = "flex";

    if (reservation.confirmed) {
        document.getElementById("confirm-lecturer-reservation").style.display = "none";
    }

    document.getElementById("lecturer-popup").style.display = "none";
    document.getElementById("student-popup").style.display = "none";
    document.getElementById("lecturer-reservation-popup").style.display = "block";

    document.getElementById("lecturer-reservation-state").innerText = `Stav: ${reservation.confirmed ? "Potvrzená" : "Nepotvrzená"}`;
    document.getElementById("lecturer-reservation-info").innerText = `Info: ${reservation.info}`;
    document.getElementById("lecturer-reservation-tag").innerText = `Tag: ${getTagNameByUUID(reservation.tag)}`;
    document.getElementById("lecturer-reservation-datetime").innerText = `Datum a čas: ${new Date(reservation.start_date).toLocaleString()} - ${new Date(reservation.end_date).toLocaleString()}`;

    document.getElementById("lecturer-reservation-first_name").innerText = `Jméno: ${reservation.student.first_name}`;
    document.getElementById("lecturer-reservation-last_name").innerText = `Příjmení: ${reservation.student.last_name}`;
    document.getElementById("lecturer-reservation-email").innerText = `Email: ${reservation.student.email}`;
    document.getElementById("lecturer-reservation-phone").innerText = `Telefon: ${reservation.student.phone_number}`;
}

function closePopup() {
    document.getElementById("popup").style.display = "none";
    selectedReservation = null;
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
            closePopup();
        });
}

function confirmReservation() {
    if (!confirm("Opravdu chcete potvrdit tuto rezervaci?")) {
        return;
    }

    fetch(`/api/reservations/confirm`, {
        method: "PUT",
        headers: {
            "Authorization": `Basic ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            reservation: selectedReservation.uuid,
            token: token
        })
    })
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
            closePopup();
            loadReservations();
        });
}

function deleteReservation() {
    if (!confirm("Opravdu chcete smazat tuto rezervaci?")) {
        return;
    }

    fetch(`/api/reservations`, {
        method: "DELETE",
        headers: {
            "Authorization": `Basic ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            reservation: selectedReservation.uuid,
            token: token
        })
    })
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
            closePopup();
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
    let startTime = document.getElementById("reservation-start-time").value;
    let endTime = document.getElementById("reservation-end-time").value;

    if (startTime == null ||
        endTime == null ||
        document.getElementById("tag-select").value == "" ||
        document.getElementById("reservation-first-name").value == "" ||
        document.getElementById("reservation-last-name").value == "" ||
        document.getElementById("reservation-email").value == "") {
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

    let tag = findInSet((p) => p.name == document.getElementById("tag-select").value, tags);
    console.log(tag);

    fetch(`/api/reservations/${uuid}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            info: document.getElementById("reservation-info").value,
            tag: tag.uuid,
            student: {
                first_name: document.getElementById("reservation-first-name").value,
                last_name: document.getElementById("reservation-last-name").value,
                email: document.getElementById("reservation-email").value,
                phone_number: document.getElementById("reservation-phone").value,
            }
        })
    })
        .then((response) => response.json())
        .then((json) => {
            console.log(json);
            loadReservations();
            closePopup();
        });
}

function compareReservationsStart(a, b) {
    if (new Date(a.start_date).getTime() < new Date(b.start_date).getTime()) {
        return -1;
    } else if (new Date(a.start_date).getTime() > new Date(b.start_date).getTime()) {
        return 1;
    }
    return 0;
}
function compareReservationsEnd(a, b) {
    if (new Date(a.end_date).getTime() < new Date(b.end_date).getTime()) {
        return -1;
    } else if (new Date(a.end_date).getTime() > new Date(b.end_date).getTime()) {
        return 1;
    }
    return 0;
}

async function getLecturers() {
    console.log("Fetching lecturer list");
    let response = fetch("/api/lecturers");
    response.catch((err) => {
        setTimeout(() => {
            getLecturers();
        }, 500);
    });
    response.then((res) => {
        const data = res.json();
        data.catch((err) => {
            setTimeout(() => {
                getLecturers();
            }, 500);
        });
        data.then((json) => {
            window.data_cache = json;
            console.log(json);
        });
    });
}

function getTags() {
    console.log("Fetching tags");
    if (data_cache == null) {
        setTimeout(() => {
            getTags();
        }, 500);
        return;
    }
    let data = new Set();
    for (let lecturer of data_cache) {
        for (let tag of lecturer.tags) {
            data.add(tag);
        }
    }
    tags = data;
    console.log(data);
    updateTags(data);
}

function updateTags(data) {
    const tag_select = document.getElementById("tag-list");
    tag_select.innerHTML = "";

    for (let tag of data) {
        const element = document.createElement("option");
        element.textContent = tag.name;

        tag_select.appendChild(element);
    }
}

function findInSet(pred, set) {
    for (let item of set) if (pred(item)) return item;
}
