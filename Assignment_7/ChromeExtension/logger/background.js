// const blockedDomains = [
//     "web.whatsapp.com",
//     "linkedin.com",
//     "netflix.com",
//     "instagram.com",
//     "facebook.com",
//     "youtube.com"
//   ];
  
//   function isBlocked(url) {
//     try {
//       const hostname = new URL(url).hostname;
//       return blockedDomains.some(domain => hostname.includes(domain));
//     } catch (e) {
//       return true;
//     }
//   }
  
//   chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
//     if (
//       changeInfo.status === "complete" &&
//       tab.url &&
//       tab.title &&
//       !isBlocked(tab.url)
//     ) {
//       const data = {
//         url: tab.url,
//         title: tab.title,
//         timestamp: new Date().toISOString()
//       };
  
//       console.log("[Tracked Visit]", data);
  
//       chrome.storage.local.get({ visits: [] }, (result) => {
//         const visits = result.visits;
//         visits.push(data);
//         chrome.storage.local.set({ visits });
//       });
//     }
//   });
  
const blockedDomains = [
    "web.whatsapp.com",
    "linkedin.com",
    "netflix.com",
    "instagram.com",
    "facebook.com",
    "youtube.com",
    "google.com",
    "http:localhost", 
    "figma.com"
  ];
  
  function isBlocked(url) {
    try {
      const hostname = new URL(url).hostname;
      return blockedDomains.some(domain => hostname.includes(domain));
    } catch (e) {
      return true;
    }
  }
  
  function isValidUrl(url) {
    // Ensure the URL is not a chrome:// or about:// URL
    return !url.startsWith("chrome://") && !url.startsWith("about://");
  }
  
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (
      changeInfo.status === "complete" &&
      tab.url &&
      tab.title &&
      !isBlocked(tab.url) &&
      isValidUrl(tab.url) // Check if URL is valid before proceeding
    ) {
      const data = {
        url: tab.url,
        title: tab.title,
        timestamp: new Date().toISOString(),
        htmlContent: ""
      };
  
      chrome.scripting.executeScript(
        {
          target: { tabId: tabId },
          func: getHtmlContent
        },
        (result) => {
          if (result && result[0] && result[0].result) {
            data.htmlContent = result[0].result;
  
            fetch('http://localhost:8000/api/visited-url-logger', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(responseData => {
              console.log("API Response:", responseData);
            })
            .catch(error => {
              console.error("Error sending data to API:", error);
            });
          }
        }
      );
  
      // Log visit in local storage
      chrome.storage.local.get({ visits: [] }, (result) => {
        const visits = result.visits;
        visits.push(data);
        chrome.storage.local.set({ visits });
      });
    }
  });
  
  // Function to get the HTML content of the page
  function getHtmlContent() {
    return document.documentElement.outerHTML;
  }
  