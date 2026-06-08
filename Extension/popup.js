const video = document.getElementById("video");

navigator.mediaDevices.getUserMedia({
    video: true
})
.then(stream => {
    video.srcObject = stream;
});

const ctx = document
    .getElementById("stressChart")
    .getContext("2d");

const data = {
    labels: [],
    datasets: [{
        label: "Stress %",
        data: [],
        borderWidth: 2
    }]
};

const chart = new Chart(ctx, {
    type: "line",
    data: data,
    options: {
        responsive: true,
        animation: false,
        scales: {
            y: {
                min: 0,
                max: 100
            }
        }
    }
});

const alertSound =
    document.getElementById("alertSound");

let lastAlert = 0;

async function updateStress() {

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/stress"
        );

        const result = await response.json();

        const stress = result.stress;
        const emotion = result.emotion;

        document.getElementById(
            "emotion"
        ).innerText =
            "Emotion: " + emotion;

        document.getElementById(
            "stress"
        ).innerText =
            "Stress: " + stress + "%";

        const time =
            new Date().toLocaleTimeString();

        data.labels.push(time);

        data.datasets[0].data.push(stress);

        if (data.labels.length > 20) {
            data.labels.shift();
            data.datasets[0].data.shift();
        }

        chart.update();

        const now = Date.now();

        if (stress >= 80 &&
            now - lastAlert > 10000) {

            alertSound.play();

            alert(
                "HIGH STRESS DETECTED!"
            );

            lastAlert = now;
        }

    } catch (err) {
        console.log(err);
    }
}

setInterval(updateStress, 2000);