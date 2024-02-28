document.addEventListener("DOMContentLoaded", () => {
    const token = getCookie("token");
    console.log("token: ", token);
    if (token == null) {
        window.location = "/login";
    }
});