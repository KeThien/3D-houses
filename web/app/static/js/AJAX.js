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
