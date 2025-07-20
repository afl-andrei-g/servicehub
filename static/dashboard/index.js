document.addEventListener('DOMContentLoaded', function() {
    const currentUrl = window.location.href;
    const menuItems = document.querySelectorAll('.sidebar-nav ul li a');

    menuItems.forEach(function(link) {
        if (link.href && currentUrl.startsWith(link.href)) {
            document.querySelectorAll('.sidebar-nav ul li').forEach(function(li) {
                li.classList.remove('active');
            });
            link.parentElement.classList.add('active');
        }
    });

    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }
    
    function checkWindowSize() {
        if (window.innerWidth <= 576) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        } else if (window.innerWidth <= 992) {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        } else {
            sidebar.classList.remove('collapsed');
            mainContent.classList.remove('expanded');
        }
    }
    
    checkWindowSize();
    window.addEventListener('resize', checkWindowSize);
    
    function simulateLoading() {
        const sections = document.querySelectorAll('.dashboard-section');
        sections.forEach((section, index) => {
            setTimeout(() => {
                section.style.opacity = '1';
                section.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    });
    
    simulateLoading();
});

text_max = (str, len) => {
    return str.length >= len ? `${str.slice(0, len)}...` : str
}

function showNoDataMessageIfEmptyById(ids) {
    ids.forEach(id => {
        const div = document.getElementById(id);
        if (div && !div.innerText.trim() && div.children.length === 0) {
            div.innerHTML = `
                <center>
                    <h3>⚠️ Nu există date în acest moment.</h3>
                </center>
            `;
        }
    });
}
