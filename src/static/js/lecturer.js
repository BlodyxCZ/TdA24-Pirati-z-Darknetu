document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("reservation-button").addEventListener("click", function() {
        let uuid = window.location.href.split("/").pop();
        console.log(uuid);
        window.location.href = `/reservations/${uuid}`;
    });
});