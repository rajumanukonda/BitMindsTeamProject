var leftBraces, rightBraces, quizJSON, parsedContent, quizHTML, score=0;

function toggleSubsections(chapterId) {
  var subsections = document.getElementById(chapterId + '-subsections');
  subsections.style.display = subsections.style.display === 'none' ? 'block' : 'none';
}

function showContent(contentId, contentTitle = "") {
  var dummyContent = document.getElementById('dummy-content');
  var dummyContentTitle = document.getElementById('dummy-content-title');

  // Show loading screen
  dummyContent.innerHTML = '<div class="loading">Loading...</div>';
  dummyContentTitle.innerHTML = contentTitle;

  // Remove previous selected class
  var selectedLink = document.querySelector('.selected');
  if (selectedLink) {
    selectedLink.classList.remove('selected');
  }

  // Add selected class to the clicked link
  var clickedLink = document.getElementById(contentId);
  if (clickedLink) {
    clickedLink.classList.add('selected');
  }

  // Fetch content from the server
  fetchContentFromServer(contentId)
    .then(function (response) {
      parsedContent = response;
      if (response.includes("```json")) {
        leftBraces = parsedContent.indexOf("```json\n{");
        rightBraces = parsedContent.indexOf("\n}\n```");
        quizJSON = JSON.parse(parsedContent.substring(leftBraces + 7, rightBraces + 2).replace(/\n/g, ''));
        console.log(quizJSON);
        window.$quizJSON = quizJSON;
      }

      // Update the content on success
      window.$response = response;

      if(quizJSON !== undefined){
        if(leftBraces !== undefined && rightBraces!==undefined){
          parsedContent = response.substr(0, leftBraces) + response.substr(rightBraces+6);
        }
        quizHTML = `<br/><br/><div id='quiz-container'><h6><u>Quiz</u></h6><p id='question'>${quizJSON.question}</p><form id="quiz-form" onsubmit='javascript:validateQuiz();return false;'>`;
        quizJSON.options.forEach(function (item, index) {
          // console.log(item, index);
          var temp = `<input type='radio' name='answer' value='${item}' id='${item}'><label for='${index}'>${item}</label><br>`;
          quizHTML += temp;
        });
        quizHTML+="<input type='submit' onsubmit='javascript:validateQuiz();' value='Submit'></form>";
        console.log(quizHTML);
        parsedContent +=quizHTML;
        console.log(contentId);
      };

      // parsedContent = response.substr(0, leftBraces) + response.substr(rightBraces + 6);
      parsedContent = parsedContent.replace(/\r/g, '').replace(/\n/g, '<br>');
      dummyContent.innerHTML = parsedContent;
      dummyContentTitle.innerHTML = contentTitle;
    })
    .catch(function (error) {
      // Handle errors
      dummyContent.innerHTML = '<div class="error">Failed to fetch content.</div>';
      dummyContentTitle.innerHTML = contentTitle;
      console.error(error);
    });
}

function validateQuiz(){
  if(document.forms["quiz-form"].answer.value == quizJSON.answer){
    score+=10;
    displayText = "Valid answer +10 points!";
  }
  else{
    score-=10;
    displayText = "Invalid answer -10 points!";
  }
  console.log(score);
  alert(displayText +" Your current score: " + score);
  document.getElementById('quiz-container').style.visibility="hidden";
  return false;
};

function fetchContentFromServer(contentId) {
  // Simulate a delay to show the loading screen
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      // Make a fetch request to the server to fetch the content
      fetch('/fetch_content?content_id=' + contentId)
        .then(function (response) {
          if (response.ok) {
            // Resolve with the response content
            resolve(response.text());
          } else {
            // Reject with an error message
            reject('Error: ' + response.status);
          }
        })
        .catch(function (error) {
          // Reject with the error
          reject(error);
        });
    }, 1000); // Adjust the delay as needed
  });
}