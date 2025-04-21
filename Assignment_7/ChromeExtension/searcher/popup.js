document.getElementById("searchTextButton").addEventListener("click", () => {
  handleSearch("text");
});

document.getElementById("searchImageButton").addEventListener("click", () => {
  handleSearch("image");
});

async function handleSearch(type) {
  const query = document.getElementById("queryInput").value.trim();
  if (!query) {
    alert("Please enter a search query");
    return;
  }

  const formData = new FormData();
  formData.append("text", query);
  formData.append("type", type);

  try {
    const response = await fetch("http://localhost:8000/api/agent-search", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    console.log("API Response:", data);

    if (!data.results?.url || !data.results?.xpath) {
      throw new Error("Invalid response: missing URL or XPath");
    }

    const { url, xpath } = data.results;
    const fixedXPath = xpath.replace("/[document][1]", "");

    // Send message to background to open tab and highlight element
    chrome.runtime.sendMessage({ url, xpath: fixedXPath });

  } catch (err) {
    console.error("Search failed:", err);
    alert("Search failed: " + err.message);
  }
}
