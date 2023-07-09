var leftBraces, rightBraces, quizJSON = new Map(), parsedContent, quizHTML, score=0, showQuiz = new Map();

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
        quizJSON.set(contentId, JSON.parse(parsedContent.substring(leftBraces + 7, rightBraces + 2).replace(/\n/g, '')));
        showQuiz.set(contentId, true);
        // console.log(quizJSON);
        // console.log(showQuiz);
        window.$quizJSON = quizJSON;
        }

      // Update the content on success
      window.$response = response;
      window.$parsedContent = parsedContent;
      window.$contentId = contentId;

      if(quizJSON.has(contentId)){
        if(leftBraces !== undefined && rightBraces!==undefined){
          parsedContent = response.substr(0, leftBraces) + response.substr(rightBraces+6);
        }
        quizHTML = `<br/><br/><div id='quiz-container' data-contentid='${contentId}'><h6><u>Quiz</u></h6><p id='question'>${quizJSON.get(contentId).question}</p><form id="quiz-form" onsubmit='javascript:validateQuiz();return false;'>`;
        quizJSON.get(contentId).options.forEach(function (item, index) {
          // console.log(item, index);
          var temp = `<input type='radio' name='answer' value='${item}' id='${item}'><label for='${index}'>${item}</label><br>`;
          quizHTML += temp;
        });
        quizHTML+="<input type='submit' onsubmit='javascript:validateQuiz();' value='Submit'></form>";
        
        // console.log(quizHTML);
        if(showQuiz.get(contentId)){
          parsedContent +=quizHTML;
        }
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
  // console.log("validateQuiz :: QID = " + document.getElementById('quiz-container').dataset.contentid);
  var contentId = document.getElementById('quiz-container').dataset.contentid;
  if(document.forms["quiz-form"].answer.value == quizJSON.get(contentId).answer){
    score+=10;
    displayText = "Valid answer +10 points!";
  }
  else{
    score-=10;
    displayText = "Invalid answer -10 points!";
  }
  // console.log(score);
  alert(displayText +" Your current score: " + score);
  document.getElementById('quiz-container').style.visibility="hidden";
  document.getElementById('score-level').innerText = "Level: Beginner | Score: " + score;
  showQuiz.set(contentId,false);
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