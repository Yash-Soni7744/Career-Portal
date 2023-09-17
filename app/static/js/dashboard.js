function truncate(str, maxlength) {
  return (str.length > maxlength) ?
    str.slice(0, maxlength - 1) + '…' : str;
}

const upcomingInterviews = document.querySelectorAll(
  ".upcoming-interviews-card"
);

upcomingInterviews[0].style.display = "flex";

var counter = 0;

const leftArrow = document.getElementById("left-slider");
const rightArrow = document.getElementById("right-slider");

leftArrow.style.fill = "#e0e0e0";

if (upcomingInterviews.length == 1) {
  rightArrow.style.fill = "#e0e0e0";
}

leftArrow.addEventListener("click", () => {
  if (upcomingInterviews.length == 1) {
    return;
  }
  rightArrow.style.fill = "#7234FE";
  if (counter > 0) {
    counter--;
    upcomingInterviews[counter + 1].style.display = "none";
    upcomingInterviews[counter].style.display = "flex";
  }
  if (counter > 0) {
    leftArrow.style.fill = "#7234FE";
  } else {
    leftArrow.style.fill = "#e0e0e0";
  }
});

rightArrow.addEventListener("click", () => {
  if (upcomingInterviews.length == 1) {
    return;
  }
  leftArrow.style.fill = "#7234FE";
  if (counter < upcomingInterviews.length - 1) {
    counter++;
    upcomingInterviews[counter - 1].style.display = "none";
    upcomingInterviews[counter].style.display = "flex";
  }
  if (counter == upcomingInterviews.length - 1) {
    rightArrow.style.fill = "#e0e0e0";
  } else {
    rightArrow.style.fill = "#7234FE";
  }
});

const jobDetails = document.querySelectorAll(".job-description-value");

for (let i = 0; i < jobDetails.length; i++) {
  if (jobDetails[i].textContent == "") {
    jobDetails[i].textContent = "Not Specified";
  }
  else if (jobDetails[i].textContent == "0") {
    jobDetails[i].textContent = "Not Specified";
  }
  else {
    jobDetails[i].textContent = truncate((jobDetails[i].textContent),300);
  }
}