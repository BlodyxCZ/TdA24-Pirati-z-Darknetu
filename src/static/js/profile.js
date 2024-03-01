document.addEventListener("DOMContentLoaded", () => {
    const token = getCookie("token");
    console.log("token: ", token);
    if (token == null) {
        window.location = "/login";
    }

    const submitButton = document.getElementById("info-change-button");
    submitButton.addEventListener("click", (e) => {
        const oldPassword = document.getElementById("old-password").value;
        const newPassword = document.getElementById("new-password").value;

        if (oldPassword == "" || newPassword == "") {
            return;
        }

        fetch(`/api/lecturers/${uuid}/password-change`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
                token: token
            })
        })
            .then((response) => response.json())
            .then((json) => {
                console.log(json);
                alert(json.message);
                window.location.reload();
            });
    });

    const emailCheckBox = document.getElementById("receive-emails");
    emailCheckBox.addEventListener("change", (e) => {
        // Blame the backend guy for the spelling
        fetch(`/api/lecturers/${uuid}/recieve-emails`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token: token,
                value: emailCheckBox.checked
            })
        })
            .then((response) => response.json())
            .then((json) => {
                console.log(json);
                alert(json.message);
            });
    });
});