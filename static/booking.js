const daysContainer = document.querySelector('.calendar_days'),
    nextBtn = document.querySelector(".next-btn"),
    prevBtn = document.querySelector(".prev-btn"),
    month = document.querySelector(".calendar_month"),
    todayBtn = document.querySelector(".today-btn");

    const bookingModal = document.getElementById("bookingModal");
    const modalClose = document.querySelector(".close");
    const checkInDateInput = document.getElementById("modal-check-in-date"); 

const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// lay ngay hien tai

const date = new Date();
let currentMonth = date.getMonth();
let currentYear = date.getFullYear();

function renderCalendar() {
    
    date.setDate(1);
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const lastDayIndex = lastDay.getDay();
    const lastDayDate = lastDay.getDate();
    const prevLastDay = new Date(currentYear, currentMonth, 0);
    const prevLastDayDate = prevLastDay.getDate();
    const nextDays = 7 - lastDayIndex - 1;

    
    month.innerHTML = `${months[currentMonth]} ${currentYear}`;

   
    let days = "";

    
    for (let x = firstDay.getDay(); x > 0; x--) {
        days += `<div class="day prev">${prevLastDayDate - x + 1}</div>`;
    }

    for (let i = 1; i <= lastDayDate; i++) {
        
        if (
            i === new Date().getDate() &&
            currentMonth === new Date().getMonth() &&
            currentYear === new Date().getFullYear()
        ) {
            
            days += `<div class="day today">${i}</div>`;
        } else {
            
            days += `<div class="day ">${i}</div>`;
        }
    }

    
    for (let j = 1; j <= nextDays; j++) {
        days += `<div class="day next">${j}</div>`;
    }

    
    hideTodayBtn();
    daysContainer.innerHTML = days;
    addDayClickEvents();
}

renderCalendar();

nextBtn.addEventListener("click", () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    renderCalendar();
});

// prev monyh btn
prevBtn.addEventListener("click", () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    renderCalendar();
});

// go to today
todayBtn.addEventListener("click", () => {
    currentMonth = date.getMonth();
    currentYear = date.getFullYear();

    renderCalendar();
});


function hideTodayBtn() {
    if (
        currentMonth === new Date().getMonth() &&
        currentYear === new Date().getFullYear()
    ) {
        todayBtn.style.display = "none";
    } else {
        todayBtn.style.display = "flex";
    }
}


function openBookingModal(selectedDate) {
    checkInDateInput.value = selectedDate; // Đặt ngày check-in
    bookingModal.style.display = "block"; 
}

// Thêm sự kiện click vào từng ngày
function addDayClickEvents() {
    document.querySelectorAll('.calendar_days .day').forEach(day => {
        day.addEventListener('click', (event) => {
            const selectedDate = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(day.textContent).padStart(2, '0')}`;
            openBookingModal(selectedDate);
        });
    });
}


modalClose.addEventListener("click", () => {
    bookingModal.style.display = "none";
});

// Đóng modal khi click ngoài modal
window.addEventListener("click", (event) => {
    if (event.target === bookingModal) {
        bookingModal.style.display = "none";
    }
});