const searchInput = document.querySelector('#grievance-search');
const statusFilter = document.querySelector('#grievance-filter');
const cards = [...document.querySelectorAll('.admin-card')];
const resultCount = document.querySelector('#result-count');
const emptyMessage = document.querySelector('#filter-empty');

if (searchInput && statusFilter) {
    const updateList = () => {
        const query = searchInput.value.trim().toLocaleLowerCase();
        const status = statusFilter.value;
        let visibleCount = 0;

        for (const card of cards) {
            const matchesQuery = card.textContent.toLocaleLowerCase().includes(query);
            const matchesStatus = status === 'all' || card.dataset.status === status;
            const isVisible = matchesQuery && matchesStatus;

            card.hidden = !isVisible;
            visibleCount += Number(isVisible);
        }

        resultCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'note' : 'notes'}`;
        emptyMessage.hidden = visibleCount !== 0;
    };

    searchInput.addEventListener('input', updateList);
    statusFilter.addEventListener('change', updateList);
}