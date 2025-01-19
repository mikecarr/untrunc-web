// Show the loading overlay when the form is submitted
function showLoading() {
    const loadingOverlay = document.getElementById("loading-overlay");
    loadingOverlay.style.display = "flex"; // Show the loading overlay
}

// Delete a file
function deleteFile(filename, rowElement) {
    fetch(`/delete/${filename}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                rowElement.remove();
                alert(data.message);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
}

// document.addEventListener("DOMContentLoaded", () => {
//     const goodFileInput = document.getElementById("good");
//     const badFileInput = document.getElementById("bad");
//     const repairButton = document.querySelector("button[type='submit']");

//     function toggleButtonState() {
//         if (goodFileInput.files.length > 0 && badFileInput.files.length > 0) {
//             repairButton.disabled = false;
//         } else {
//             repairButton.disabled = true;
//         }
//     }

//     // Attach event listeners to file inputs
//     goodFileInput.addEventListener("change", toggleButtonState);
//     badFileInput.addEventListener("change", toggleButtonState);

//     // Disable the button initially
//     repairButton.disabled = true;
// });

document.addEventListener("DOMContentLoaded", () => {
    const goodFileInput = document.getElementById("good");
    const badFileInput = document.getElementById("bad");
    const repairButton = document.querySelector("button[type='submit']");

    function toggleButtonState() {
        if (goodFileInput.files.length > 0 && badFileInput.files.length > 0) {
            repairButton.disabled = false;
        } else {
            repairButton.disabled = true;
        }
    }

    function resetForm() {
        // Clear file inputs
        goodFileInput.value = "";
        badFileInput.value = "";
        
        // Disable the repair button
        repairButton.disabled = true;
    }

    // Attach event listeners to file inputs
    goodFileInput.addEventListener("change", toggleButtonState);
    badFileInput.addEventListener("change", toggleButtonState);

    // Disable the button initially
    repairButton.disabled = true;

    // Expose resetForm globally for the reset button
    window.resetForm = resetForm;
});
