// document.getElementById("searchTextButton").addEventListener("click", () => {
//   handleSearch("text");
// });

// document.getElementById("searchImageButton").addEventListener("click", () => {
//   handleSearch("image");
// });

// async function handleSearch(type) {
//   const query = document.getElementById("queryInput").value.trim();
//   const loader = document.getElementById("loader");

//   if (!query) {
//     alert("Please enter a search query");
//     return;
//   }

//   loader.style.display = "block"; // Show loader

//   const formData = new FormData();
//   formData.append("text", query);
//   formData.append("type", type);

//   try {
//     const response = await fetch("http://localhost:8000/api/agent-search", {
//       method: "POST",
//       body: formData
//     });

//     const data = await response.json();
//     console.log("API Response:", data);

//     if (!data.results?.url || !data.results?.xpath) {
//       throw new Error("Invalid response: missing URL or XPath");
//     }

//     const { url, xpath } = data.results;
//     const fixedXPath = xpath.replace("/[document][1]", "");

//     chrome.runtime.sendMessage({ url, xpath: fixedXPath });

//   } catch (err) {
//     console.error("Search failed:", err);
//     alert("Search failed: " + err.message);
//   } finally {
//     loader.style.display = "none"; // Hide loader in all cases
//   }
// }

document.getElementById("searchTextButton").addEventListener("click", () => {
  handleSearch("text");
});

document.getElementById("searchImageButton").addEventListener("click", () => {
  handleSearch("image");
});

document.getElementById("uploadImageButton").addEventListener("click", () => {
  handleImageUploadSearch();
});

async function handleSearch(type) {
  const query = document.getElementById("queryInput").value.trim();
  const loader = document.getElementById("loader");

  if (!query) {
    alert("Please enter a search query");
    return;
  }

  const formData = new FormData();
  formData.append("text", query);
  formData.append("type", type);

  loader.style.display = "block"; // Show loader

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

    chrome.runtime.sendMessage({ url, xpath: fixedXPath });

  } catch (err) {
    console.error("Search failed:", err);
    alert("Search failed: " + err.message);
  } finally {
    loader.style.display = "none"; // Hide loader
  }
}

async function handleImageUploadSearch() {
  const fileInput = document.getElementById("imageInput");
  const file = fileInput.files[0];
  const loader = document.getElementById("loader");

  if (!file) {
    alert("Please select an image");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("type", "image");

  loader.style.display = "block"; // Show loader

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

    chrome.runtime.sendMessage({ url, xpath: fixedXPath });

  } catch (err) {
    console.error("Image search failed:", err);
    alert("Image search failed: " + err.message);
  } finally {
    loader.style.display = "none"; 
  }
}

