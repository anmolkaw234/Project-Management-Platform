function setShowDeleteConfirmation() {
    document.getElementById('deleteConfirmation').style.display = 'block';
}

function hideDeleteConfirmation() {
    document.getElementById('deleteConfirmation').style.display = 'none';
}

function confirmDeleteProject(projectTitle) {
    console.log('Confirmed delete project:', projectTitle);
    document.getElementById('deleteConfirmation').style.display = 'none';
}