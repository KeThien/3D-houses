// document.addEventListener("DOMContentLoaded", () => {
//   // run a function for each button
//   document.querySelectorAll("button").forEach((button) => {
//     // run a function when any button is clicked
//     button.onclick = () => {
//       //new AJAX request
//       const request = new XMLHttpRequest();

//       // to the endpoint `${button.id}` with method 'POST'
//       request.open("POST", `/${button.id}`);

//       //what to do after receiving response
//       request.onload = () => {
//         //get the response text
//         const response = request.responseText;

//         //replace the vote count with the updated number of votes
//         document.getElementById("count").innerHTML = response;
//       };

//       //actually send the request
//       request.send();
//     };
//   });
// });

const buttonSubmit = document.getElementById("calculate")
const loading = document.getElementById("loading")
const myForm = document.getElementById("myForm")
const squareHolder = document.getElementById("square-holder")
const buttonLoad3d = document.getElementById("btn-load3d")

myForm.addEventListener("submit", () => {
    buttonSubmit.classList.add("disabled")
    loading.classList.remove("d-none")
    myCanvas.classList.add("d-none")
    txt = document.createTextNode("Calculation in progress...")
    document.getElementById("prediction-text").textContent = "Calculation in progress..."
    if (squareHolder) {
        squareHolder.classList.add("d-none")
    }
})
// buttonLoad3d.addEventListener("click", () => {
//     //new AJAX request
//     const request = new XMLHttpRequest();
//     request.open("POST", `/load3d`);
    
//     request.onload = () => {
//     //get the response text
//     const response = request.responseText;

//     };
    
//      //actually send the request
//     request.send();
// })
async function btn_load3d() {
    console.log("prout");
    loading.classList.remove("d-none")
    buttonSubmit.classList.add("disabled")
    buttonLoad3d.classList.add("disabled")
    myCanvas.classList.add("d-none")
    squareHolder.classList.add("d-none")
    
    fetch('/load3d', {
        method: 'POST'
    }).then((response)=>{
        console.log('blob');
        loading.classList.add("d-none")
        buttonSubmit.classList.remove("disabled")
        buttonLoad3d.classList.remove("disabled")
        myCanvas.classList.remove("d-none")
    })
}