function toggleSubsections(chapterId) {
  var subsections = document.getElementById(chapterId + '-subsections');
  subsections.style.display = subsections.style.display === 'none' ? 'block' : 'none';
}

function showContent(contentId, contentTitle = "") {
  var dummyContent = document.getElementById('dummy-content');
  var dummyContentTitle = document.getElementById('dummy-content-title');

  var leftBraces = 0, rightBraces = 0, quizJSON, parsedContent, quizHTML;

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
      if (response.includes("```json")) {
        leftBraces = response.indexOf("```json\n{");
        rightBraces = response.indexOf("\n}\n```");
        quizJSON = JSON.parse(response.substring(leftBraces + 7, rightBraces + 2).replace(/\n/g, ''));
        console.log(quizJSON);
        window.$quizJSON = quizJSON;
      }

      // Update the content on success
      window.$response = response;

      if (quizJSON) {
        quizHTML = "<div id='quiz-container'><br/><p id='question'>" + quizJSON.question + "</p>";
      }

      parsedContent = response.substr(0, leftBraces) + response.substr(rightBraces + 4);
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