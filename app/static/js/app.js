const askButton = document.getElementById("askButton");

const clearButton =
    document.getElementById("clearButton");

const clearSidebarButton =
    document.getElementById("clearSidebarButton");


const employeeIdInput =
    document.getElementById("employeeId");

const questionInput =
    document.getElementById("question");


const responseBox =
    document.getElementById("response");

const historyBox =
    document.getElementById("history");


const profileEmployee =
    document.getElementById("profileEmployee");


const quickQuestions =
    document.querySelectorAll(".quick-question");


/* =========================
   DISPLAY CONVERSATION
   ========================= */

function displayHistory(history) {

    if (!history || history.length === 0) {

        historyBox.innerHTML = `
            <div class="welcome-card">

                <div class="welcome-icon">
                    ✈️
                </div>

                <div>

                    <h3>
                        How can I help with your travel?
                    </h3>

                    <p>
                        Ask me about travel eligibility,
                        expenses, reimbursements, flights,
                        hotels, airport trips, and company
                        travel policies.
                    </p>

                </div>

            </div>
        `;

        return;
    }


    historyBox.innerHTML = "";


    history.forEach(message => {

        const messageContainer =
            document.createElement("div");


        const isUser =
            message.role === "user";


        messageContainer.className =
            isUser
                ? "message user"
                : "message assistant";


        const avatar =
            document.createElement("div");


        avatar.className =
            "message-avatar";


        avatar.textContent =
            isUser
                ? "👤"
                : "✈️";


        const content =
            document.createElement("div");


        content.className =
            "message-content";


        content.textContent =
            message.content;


        messageContainer.appendChild(
            avatar
        );


        messageContainer.appendChild(
            content
        );


        historyBox.appendChild(
            messageContainer
        );

    });


    historyBox.scrollTop =
        historyBox.scrollHeight;
}


/* =========================
   ASK QUESTION
   ========================= */

async function askQuestion() {

    const employeeId =
        employeeIdInput.value.trim();


    const question =
        questionInput.value.trim();


    if (!question) {

        responseBox.className =
            "response-status";


        responseBox.textContent =
            "Please enter a question.";


        return;
    }


    responseBox.className =
        "response-status";


    responseBox.textContent =
        "Thinking...";


    askButton.disabled = true;


    try {

        const response =
            await fetch("/ask", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    employee_id:
                        employeeId,

                    question:
                        question

                })

            });


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Unable to process your question."
            );

        }


        responseBox.textContent = "";


        displayHistory(
            data.history
        );


        questionInput.value = "";


    } catch (error) {

        responseBox.className =
            "response-status";


        responseBox.textContent =
            "Assistant unavailable: " +
            error.message;


    } finally {

        askButton.disabled = false;

    }

}


/* =========================
   CLEAR CONVERSATION
   ========================= */

async function clearConversation() {

    try {

        const response =
            await fetch("/clear", {

                method: "POST"

            });


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Unable to clear conversation."
            );

        }


        responseBox.className =
            "response-status";


        responseBox.textContent = "";


        displayHistory(
            data.history
        );


        questionInput.value = "";


    } catch (error) {

        responseBox.className =
            "response-status";


        responseBox.textContent =
            "Error: " +
            error.message;

    }

}


/* =========================
   QUICK QUESTIONS
   ========================= */

quickQuestions.forEach(button => {

    button.addEventListener(
        "click",
        function () {

            questionInput.value =
                this.textContent.trim();


            questionInput.focus();

        }
    );

});


/* =========================
   EMPLOYEE PROFILE
   ========================= */

if (employeeIdInput) {

    employeeIdInput.addEventListener(
        "input",
        function () {

            const employeeId =
                this.value.trim();


            if (employeeId) {

                profileEmployee.textContent =
                    employeeId;

            } else {

                profileEmployee.textContent =
                    "Not selected";

            }

        }
    );

}


/* =========================
   BUTTON EVENTS
   ========================= */

if (askButton) {

    askButton.addEventListener(
        "click",
        askQuestion
    );

}


if (clearButton) {

    clearButton.addEventListener(
        "click",
        clearConversation
    );

}


if (clearSidebarButton) {

    clearSidebarButton.addEventListener(
        "click",
        clearConversation
    );

}


/* =========================
   ENTER TO SEND
   ========================= */

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                askQuestion();

            }

        }
    );

}