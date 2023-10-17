/**
 * Remove "collapsed" class from navigation links on click
 */
document.addEventListener("DOMContentLoaded", function () {
  // Get the current URL path
  var currentUrl = window.location.pathname;

  // Select all navigation links with class "nav-link"
  var navLinks = document.querySelectorAll(".nav-link");

  // Loop through each link
  navLinks.forEach(function (link) {
    var linkUrl = link.getAttribute("href");

    // Check if the link has list items (a sibling UL element)
    var hasListItems = link.nextElementSibling && link.nextElementSibling.tagName === "ul";

    // Check if the current URL matches the link URL and it doesn't have list items
    if (!hasListItems && currentUrl === linkUrl) {
      // Remove the "collapsed" class from the link
      link.classList.remove("collapsed");
    }
  });
});
