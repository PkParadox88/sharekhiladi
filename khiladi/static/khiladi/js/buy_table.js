document.addEventListener("DOMContentLoaded", function () {
  const refreshButton = document.getElementById("refresh-button");
  const loadingSpinner = document.getElementById("loading-spinner");

  refreshButton.addEventListener("click", async () => {
    // Show the loading spinner while a function is called
    loadingSpinner.classList.remove("hidden");

    // Call your function here
    await fetchData();

    // Hide the loading spinner when the function is done
    loadingSpinner.classList.add("hidden");
  });

  // Example function to fetch data (replace with your actual data retrieval logic)
  async function fetchData() {
    // Get the current URL
    const currentUrl = window.location.href;

    // Check if "/refresh" is already present at the end of the URL
    if (!currentUrl.endsWith('/refresh')) {
      // Append "/refresh" to the current URL
      const refreshUrl = currentUrl + '/refresh';

      // Navigate to the new URL to refresh the page
      window.location.href = refreshUrl;
    }

    // Simulate a delay (you can replace this with your actual data fetching logic)
    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
});
