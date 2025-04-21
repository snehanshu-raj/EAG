chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.url && message.xpath) {
    const { url, xpath } = message;

    // Open the URL in a new tab
    chrome.tabs.create({ url, active: true }, (newTab) => {
      const onTabUpdated = (tabId, changeInfo) => {
        if (tabId === newTab.id && changeInfo.status === "complete") {
          chrome.tabs.onUpdated.removeListener(onTabUpdated);

          console.log("Tab loaded, injecting script...");

          // First, let's inject a simple alert to verify if the script can run
          chrome.scripting.executeScript({
            target: { tabId: newTab.id },
            func: () => {
              alert("Element located!");
              console.log("[Injected Script] Script injected!");
            }
          }).then(() => {
            console.log("[Injected Script] Test injection successful.");
          }).catch(err => {
            console.error("[Injected Script] Test injection failed:", err);
          });

          // After confirming injection works, we'll inject the real script
          // chrome.scripting.executeScript({
          //   target: { tabId: newTab.id },
          //   func: (xpathStr) => {
          //     try {
          //       console.log("[Injected Script] Evaluating XPath:", xpathStr);
          
          //       const result = document.evaluate(
          //         xpathStr,
          //         document,
          //         null,
          //         XPathResult.FIRST_ORDERED_NODE_TYPE,
          //         null
          //       );
          
          //       const element = result.singleNodeValue;
          
          //       if (element) {
          //         console.log("[Injected Script] Element found:", element);
          
          //         element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          
          //         // Ensure the element is visible
          //         const computedStyle = window.getComputedStyle(element);
          //         if (computedStyle.display === "none") {
          //           element.style.display = "block";
          //         }
          //         if (computedStyle.visibility === "hidden") {
          //           element.style.visibility = "visible";
          //         }
          //         if (computedStyle.opacity === "0") {
          //           element.style.opacity = "1";
          //         }
          
          //         // Highlight with a flashing border overlay
          //         const highlightBox = document.createElement("div");
          //         const rect = element.getBoundingClientRect();
          
          //         Object.assign(highlightBox.style, {
          //           position: "absolute",
          //           top: `${window.scrollY + rect.top}px`,
          //           left: `${window.scrollX + rect.left}px`,
          //           width: `${rect.width}px`,
          //           height: `${rect.height}px`,
          //           border: "4px solid red",
          //           zIndex: "999999",
          //           pointerEvents: "none",
          //           animation: "highlight-pulse 1s ease-in-out infinite",
          //         });
          
          //         const style = document.createElement("style");
          //         style.textContent = `
          //           @keyframes highlight-pulse {
          //             0% { box-shadow: 0 0 10px 5px red; }
          //             50% { box-shadow: 0 0 10px 2px red; }
          //             100% { box-shadow: 0 0 10px 5px red; }
          //           }
          //         `;
          //         document.head.appendChild(style);
          //         document.body.appendChild(highlightBox);
          
          //         setTimeout(() => {
          //           highlightBox.remove();
          //           style.remove();
          //         }, 30000);
          
          //       } else {
          //         console.error("[Injected Script] Element not found");
          //         alert("Element not found for the given XPath.");
          //       }
          //     } catch (e) {
          //       console.error("[Injected Script] Error:", e);
          //     }
          //   },
          //   args: [xpath]
          
          // }).then(() => {
          //   console.log("[Injected Script] Enhanced highlighting injected successfully.");
          // }).catch(err => {
          //   console.error("[Injected Script] Enhanced highlighting injection failed:", err);
          // });

          chrome.scripting.executeScript({
            target: { tabId: newTab.id },
            func: async (xpathStr) => {
              function waitForElement(xpath, timeout = 5000) {
                return new Promise((resolve, reject) => {
                  const interval = 200;
                  const startTime = Date.now();
          
                  const check = () => {
                    const result = document.evaluate(
                      xpath,
                      document,
                      null,
                      XPathResult.FIRST_ORDERED_NODE_TYPE,
                      null
                    );
                    let el = result.singleNodeValue;
          
                    // If it's a text node, go to parent
                    if (el && el.nodeType === Node.TEXT_NODE) el = el.parentElement;
          
                    // Climb up if too small (height/width < 5px)
                    let candidate = el;
                    while (candidate && (candidate.offsetHeight < 5 || candidate.offsetWidth < 5)) {
                      candidate = candidate.parentElement;
                    }
          
                    el = candidate || el;
          
                    if (el && el.offsetHeight > 0 && el.offsetWidth > 0) {
                      resolve(el);
                    } else if (Date.now() - startTime >= timeout) {
                      reject("Element not found or visible in time.");
                    } else {
                      setTimeout(check, interval);
                    }
                  };
          
                  check();
                });
              }
          
              try {
                console.log("[Injected Script] Waiting for element...");
          
                const element = await waitForElement(xpathStr);
                element.scrollIntoView({ behavior: "smooth", block: "center" });
          
                // Ensure visibility
                const computedStyle = window.getComputedStyle(element);
                if (computedStyle.display === "none") element.style.display = "block";
                if (computedStyle.visibility === "hidden") element.style.visibility = "visible";
                if (computedStyle.opacity === "0") element.style.opacity = "1";
          
                // Ensure relative positioning
                if (window.getComputedStyle(element).position === "static") {
                  element.style.position = "relative";
                }
          
                // Highlight box
                const highlight = document.createElement("div");
                Object.assign(highlight.style, {
                  position: "absolute",
                  top: "0",
                  left: "0",
                  width: "100%",
                  height: "100%",
                  border: "10px solid red",
                  boxSizing: "border-box",
                  zIndex: "9999",
                  animation: "flash-border 1s infinite",
                  pointerEvents: "none"
                });
          
                // Animation style
                const styleTag = document.createElement("style");
                styleTag.textContent = `
                  @keyframes flash-border {
                    0% { border-color: red; }
                    50% { border-color: green; }
                    100% { border-color: red; }
                  }
                `;
                document.head.appendChild(styleTag);
                element.appendChild(highlight);
          
                setTimeout(() => {
                  highlight.remove();
                  styleTag.remove();
                }, 30000);
          
                console.log("[Injected Script] Highlight added to element.");
              } catch (err) {
                console.error("[Injected Script] Error:", err);
                alert("Highlight failed: " + err);
              }
            },
            args: [xpath]
          });          
                    
        }
      };
      chrome.tabs.onUpdated.addListener(onTabUpdated);
    });
  }
});
