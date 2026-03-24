async function predict() {
    const title = document.getElementById("title").value;

    const response = await fetch("http://127.0.0.1:8000/predict?title=" + title, {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    });

    const data = await response.json();

    document.getElementById("result").innerText =
        "Predicted Genre: " + data.predicted_genre;
}