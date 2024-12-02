let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let timer;

console.log("Script loaded");

async function fetchQuestions(difficulty) {
    console.log(`Fetching questions for difficulty: ${difficulty}`);
    const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ difficulty }),
    });
    questions = await response.json();
    console.log("Questions received:", questions); // Debugging log
    startQuiz();
}

function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    document.getElementById("score").textContent = `Score: ${score}`;
    showQuestion();
}

function showQuestion() {
    if (currentQuestionIndex >= questions.length) {
        alert(`Quiz Over! Your final score is ${score}.`);
        return;
    }

    // Get the current question
    const question = questions[currentQuestionIndex];

    // Display the sentence with a dropbox
    document.getElementById("question").innerHTML = question.sentence.replace(
        /___+/g,
        '<span class="dropbox" id="dropbox">______</span>'
    );

    // Display the draggable options
    const optionsDiv = document.getElementById("options");
    optionsDiv.innerHTML = ""; // Clear previous options

    question.options.forEach((option) => {
        const button = document.createElement("div");
        button.textContent = option;
        button.className = "option-button";
        button.draggable = true;

        // Drag Start Event
        button.ondragstart = (event) => {
            event.dataTransfer.setData("text", option);
        };

        optionsDiv.appendChild(button);
    });

    // Make the dropbox droppable
    const dropbox = document.getElementById("dropbox");

    dropbox.ondragover = (event) => {
        event.preventDefault();
        dropbox.style.borderColor = "#007bff";
    };

    dropbox.ondragleave = () => {
        dropbox.style.borderColor = "#ccc";
    };

    dropbox.ondrop = (event) => {
        event.preventDefault();
        const droppedOption = event.dataTransfer.getData("text");

        // Check if the answer is correct
        if (droppedOption === question.correct_option) {
            dropbox.textContent = droppedOption;
            dropbox.classList.add("correct");
            dropbox.classList.remove("incorrect");
            score++;
            document.getElementById("score").textContent = `Score: ${score}`;
        } else {
            dropbox.textContent = droppedOption;
            dropbox.classList.add("incorrect");
            dropbox.classList.remove("correct");
        }

        // Show "Next" button after drop
        document.getElementById("next-question").style.display = "block";
    };

    // Hide the "Next" button initially
    document.getElementById("next-question").style.display = "none";

    // Reset and start the timer
    startTimer(30);
}

// Show loading spinner before the next question
document.getElementById("next-question").onclick = () => {
    document.getElementById("loading-spinner").style.display = "block";

    // Simulate loading delay
    setTimeout(() => {
        document.getElementById("loading-spinner").style.display = "none";
        currentQuestionIndex++;
        showQuestion();
    }, 1000);
};



function handleAnswer(selectedOption, correctAnswer) {
    if (selectedOption === correctAnswer) {
        score++;
        document.getElementById("score").textContent = `Score: ${score}`;
    }
    document.getElementById("next-question").style.display = "block";
}

function startTimer(seconds) {
    clearInterval(timer);
    const timerDiv = document.getElementById("timer");
    timerDiv.textContent = `Timer: ${seconds}s`;

    timer = setInterval(() => {
        seconds--;
        timerDiv.textContent = `Timer: ${seconds}s`;
        if (seconds <= 0) {
            clearInterval(timer);
            alert("Time's up!");
            document.getElementById("next-question").style.display = "block";
        }
    }, 1000);
}

document.getElementById("next-question").onclick = () => {
    currentQuestionIndex++;
    showQuestion();
};

// Automatically fetch questions when the script is loaded
if (typeof difficulty !== "undefined") {
    fetchQuestions(difficulty);
} else {
    console.error("Difficulty level not defined!");
}
