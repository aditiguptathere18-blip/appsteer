const clientForms = {

    "Acko": [
        { label: "Type of Activity", name: "type_of_activity", type: "dropdown", options: ["Audit cases", "Meeting"] },

        { label: "Exact Nature", name: "exact_nature", type: "dropdown", options: ["Audit", "Internal", "Client Meeting"] },

        { label: "Policy Num or Name", name: "policy_number", type: "text" },

        { label: "No. Cases", name: "no_cases", type: "number", default: 0 },

        { label: "Sum Assured", name: "sum_assured", type: "number" },

        { label: "Decision", name: "decision", type: "dropdown", options: ["OK", "Not OK", "Others"] },

        { label: "Duration (mins)", name: "duration", type: "number" }
    ],

    "Break time": [
        { label: "Duration (mins)", name: "duration", type: "number" },

        { label: "Remarks", name: "remarks", type: "text" }
    ]
};


let currentClient = null;

let activityCount = 0;

let currentSlide = 0;


// 🔥 ADD ACTIVITY
function addActivity() {

    let client = document.getElementById("clientSelect").value;

    if (!client) {
        alert("Please select client first");
        return;
    }

    let container = document.getElementById("activitiesContainer");

    // CLIENT CHANGE
    if (currentClient && currentClient !== client) {

        if (!confirm("Changing client will remove previous activities")) {
            return;
        }

        container.innerHTML = "";

        activityCount = 0;

        currentSlide = 0;
    }

    currentClient = client;

    let activityDiv = document.createElement("div");

    activityDiv.classList.add("activity-slide");

    activityDiv.id = `activity_${activityCount}`;

    // HIDE NEW SLIDES
    activityDiv.style.display = "none";

    activityDiv.style.border = "1px solid black";
    activityDiv.style.padding = "15px";
    activityDiv.style.marginTop = "10px";

    let fields = clientForms[client];

    let html = `<h3>${client} - Activity ${activityCount + 1}</h3>
        <input type ="hidden" name="client_name[]" value="${client}">`;

    fields.forEach(field => {

        // DROPDOWN
        if (field.type === "dropdown") {

            html += `
                <label>${field.label}</label><br>

                <select name="${field.name}[]">

                    ${field.options.map(opt =>
                        `<option value="${opt}">${opt}</option>`
                    ).join("")}

                </select>

                <br><br>
            `;
        }

        // INPUT
        else {

            html += `
                <label>${field.label}</label><br>

                <input 
                    type="${field.type}"
                    name="${field.name}[]"
                    value="${field.default || ''}"
                >

                <br><br>
            `;
        }
    });

    // AUTO DATE
    let today = new Date().toISOString().split('T')[0];

    html += `
        <label>Activity Date</label><br>

        <input 
            type="date"
            name="activity_date[]"
            value="${today}"
            readonly
        >

        <br><br>
    `;

    // DELETE BUTTON
    html += `
        <button 
            type="button"
            onclick="deleteActivity(${activityCount})"
        >
            Delete
        </button>
    `;

    activityDiv.innerHTML = html;

    container.appendChild(activityDiv);

    activityCount++;

    showSlide(activityCount - 1);
}


// 🔥 SHOW CURRENT SLIDE
function showSlide(index) {

    let slides = document.querySelectorAll(".activity-slide");

    slides.forEach(slide => {
        slide.style.display = "none";
    });

    if (slides[index]) {
        slides[index].style.display = "block";
        currentSlide = index;
    }
}


// 🔥 NEXT
function nextActivity() {

    let slides = document.querySelectorAll(".activity-slide");

    if (currentSlide < slides.length - 1) {
        showSlide(currentSlide + 1);
    }
}


// 🔥 PREVIOUS
function previousActivity() {

    if (currentSlide > 0) {
        showSlide(currentSlide - 1);
    }
}


// 🔥 DELETE
function deleteActivity(id) {

    let element = document.getElementById(`activity_${id}`);

    if (element) {
        element.remove();
    }

    let slides = document.querySelectorAll(".activity-slide");

    if (slides.length > 0) {

        if (currentSlide >= slides.length) {
            currentSlide = slides.length - 1;
        }

        showSlide(currentSlide);
    }
}
//Change Client
function changeClient() {
    let container = document.getElementById("activitiesContainer");
    // CLEAR OLD ACTIVITIES
    container.innerHTML = "";
    activityCount = 0;
    currentSlide = 0;
    // AUTO CREATE FIRST ACTIVITY
    addActivity();
}