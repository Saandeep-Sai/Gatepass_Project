// script.js

// ✅ Show success/error messages dynamically
function showMessage(message, type = "success") {
    const msgBox = document.getElementById("message");
    if (msgBox) {
        msgBox.innerText = message;
        msgBox.className = type; // "success" or "error"
        msgBox.style.display = "block";

        setTimeout(() => {
            msgBox.style.display = "none";
        }, 3000);
    }
}

// ✅ Validate Registration Form
function validateRegisterForm() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirm_password").value.trim();

    if (username === "" || password === "" || confirmPassword === "") {
        showMessage("All fields are required!", "error");
        return false;
    }

    if (password !== confirmPassword) {
        showMessage("Passwords do not match!", "error");
        return false;
    }

    return true; // allow form submission
}

// ✅ Validate Login Form
function validateLoginForm() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (username === "" || password === "") {
        showMessage("Username and Password are required!", "error");
        return false;
    }

    return true;
}

// ✅ Role Redirection (Student, Faculty, Security)
function redirectToRole(role) {
    if (role === "student") {
        window.location.href = "/student";
    } else if (role === "faculty") {
        window.location.href = "/faculty";
    } else if (role === "security") {
        window.location.href = "/security";
    } else {
        showMessage("Invalid role!", "error");
    }
}
