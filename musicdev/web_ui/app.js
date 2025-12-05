document.addEventListener("DOMContentLoaded", () => {
    const captureBtn = document.getElementById("captureBtn");
    const textBtn = document.getElementById("textBtn");
    const textInput = document.getElementById("textInput");
    const result = document.getElementById("result");
    const loading = document.getElementById("loading");

    const video = document.getElementById("camera");
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    // ========== CAMERA SETUP ==========
    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            video.srcObject = stream;
        } catch (err) {
            console.error("Camera error:", err);
            result.innerHTML = `<p class="error">Camera access blocked!</p>`;
        }
    }

    startCamera();

    function takeSnapshot() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return new Promise(resolve => canvas.toBlob(resolve, "image/png"));
    }

    // ========== IMAGE MOOD ANALYSIS ==========
    captureBtn.addEventListener("click", async () => {
        result.classList.add("hidden");
        loading.classList.remove("hidden");

        const imgBlob = await takeSnapshot();
        const formData = new FormData();
        formData.append("image", imgBlob, "capture.png");

        const res = await fetch("/analyze-image", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        loading.classList.add("hidden");

        if (data.error) {
            result.classList.remove("hidden");
            result.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        result.classList.remove("hidden");
        result.innerHTML = `
            <p>Your mood: <strong>${data.mood}</strong></p>
            <p>Opening playlist...</p>
        `;

        window.open(data.playlist, "_blank");
    });

    // ========== TEXT MOOD ANALYSIS ==========
    textBtn.addEventListener("click", async () => {
        const txt = textInput.value.trim();
        if (!txt) {
            result.classList.remove("hidden");
            result.innerHTML = `<p class="error">Type something!</p>`;
            return;
        }

        loading.classList.remove("hidden");
        result.classList.add("hidden");

        const res = await fetch("/analyze-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_text: txt })
        });

        const data = await res.json();
        loading.classList.add("hidden");

        if (data.error) {
            result.classList.remove("hidden");
            result.innerHTML = `<p class="error">${data.error}</p>`;
            return;
        }

        result.classList.remove("hidden");
        result.innerHTML = `
            <p>Your mood: <strong>${data.mood}</strong></p>
            <p>Opening playlist...</p>
        `;

        window.open(data.playlist, "_blank");
    });
});
