function formatGenres(rawGenre) {
    // Split by common separators (; or ,)
    let genres = rawGenre.split(/[,;]+/);

    // Normalize (trim + lowercase)
    genres = genres.map(g => g.trim().toLowerCase());

    // Remove duplicates
    genres = [...new Set(genres)];

    // Capitalize nicely
    genres = genres.map(g =>
        g.split(' ')
         .map(word => word.charAt(0).toUpperCase() + word.slice(1))
         .join(' ')
    );

    // Limit to 3 genres (keeps UI clean)
    genres = genres.slice(0, 3);

    // Join with nice separator
    return genres.join(" • ");
}

function getCrowReaction(genre) {
    genre = genre.toLowerCase();

    if (genre.includes("history")) {
        return {
            emoji: "🐦‍⬛📜",
            message: "Ah… tales of the past...",
            className: "smart"
        };
    }

    if (genre.includes("romance")) {
        return {
            emoji: "🐦‍⬛💕",
            message: "Love is in the air...",
            className: "romantic"
        };
    }

    if (genre.includes("horror")) {
        return {
            emoji: "🐦‍⬛👁️",
            message: "Something lurks in the shadows...",
            className: "spooky"
        };
    }

    if (genre.includes("fantasy")) {
        return {
            emoji: "🐦‍⬛✨",
            message: "Magic flows through these pages...",
            className: "happy"
        };
    }

    if (genre.includes("science")) {
        return {
            emoji: "🐦‍⬛🧪",
            message: "Knowledge is power...",
            className: "smart"
        };
    }

    return {
        emoji: "🐦‍⬛📖",
        message: "An interesting choice...",
        className: ""
    };
}

async function predict() {
    const titleInput = document.getElementById("title");
    const result = document.getElementById("result");
    const crow = document.getElementById("crow");
    const crowMessage = document.getElementById("crow-message");

    const title = titleInput.value;

    if (!title.trim()) {
        result.innerText = "Please enter a title!";
        return;
    }

    // Reset all classes
    crow.classList.remove("thinking", "happy", "spooky", "smart", "romantic");

    // Thinking state 🧠
    result.innerText = "The crow is thinking...";
    crow.classList.add("thinking");
    crowMessage.innerText = "";

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/predict?title=${encodeURIComponent(title)}`
        );

        const data = await response.json();

        const rawGenre = data.predicted_genre;

        // ✨ Clean + format genres
        const formattedGenre = formatGenres(rawGenre);

        result.innerText = "📚 Genre: " + formattedGenre;

        // Use cleaned genre for reaction
        const reaction = getCrowReaction(formattedGenre);

        // Apply reaction 🐦‍⬛✨
        crow.innerText = reaction.emoji;

        crow.classList.remove("thinking");

        if (reaction.className) {
            crow.classList.add(reaction.className);
        }

        crowMessage.innerText = reaction.message;

    } catch (error) {
        result.innerText = "Something went wrong...";
        crow.classList.remove("thinking");
    }
}