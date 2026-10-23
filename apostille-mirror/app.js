document.addEventListener('DOMContentLoaded', () => {
    const setText = (node, value) => {
        if (node) {
            node.textContent = value ?? '';
        }
    };

    const createSafeListItem = (node) => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        const slug = String(node?.id || node?.title || '').trim();
        const href = slug ? `nodes/${encodeURI(slug)}.html` : '#';

        link.href = href;
        if (node?.icon) {
            const icon = document.createElement('span');
            icon.setAttribute('aria-hidden', 'true');
            icon.textContent = node.icon;
            link.appendChild(icon);
            link.appendChild(document.createTextNode(' '));
        }
        link.appendChild(document.createTextNode(String(node?.title || 'Evidence node')));
        item.appendChild(link);
        return item;
    };

    const createSafeEvidenceCard = (node) => {
        const article = document.createElement('article');
        article.className = 'ev-card';
        article.tabIndex = 0;
        article.setAttribute('role', 'article');
        article.setAttribute('aria-label', String(node?.title || 'Evidence node'));

        const icon = document.createElement('div');
        icon.className = 'ev-card-icon';
        icon.setAttribute('aria-hidden', 'true');
        icon.textContent = node?.icon || '•';

        const title = document.createElement('div');
        title.className = 'ev-card-title';
        title.textContent = node?.title || 'Evidence node';

        const body = document.createElement('div');
        body.className = 'ev-card-body';

        if (node?.num) {
            const num = document.createElement('span');
            num.className = 'num';
            num.textContent = String(node.num);
            body.appendChild(num);
        }

        const content = document.createElement('span');
        content.textContent = node?.body || '';
        body.appendChild(content);

        article.appendChild(icon);
        article.appendChild(title);
        article.appendChild(body);
        return article;
    };

    const createSafeProjectionCard = (item) => {
        const card = document.createElement('div');
        card.className = 'proj-card';
        card.setAttribute('role', 'region');
        card.setAttribute('aria-label', String(item?.title || 'Projection'));

        const badge = document.createElement('div');
        badge.className = 'proj-badge';
        badge.textContent = item?.badge || item?.kind || 'Projection';

        const title = document.createElement('div');
        title.className = 'proj-title';
        title.textContent = item?.title || 'Projection';

        const preview = document.createElement('div');
        preview.className = 'proj-preview';
        preview.textContent = item?.preview || '';

        const actions = document.createElement('div');
        actions.className = 'proj-actions';

        const openLink = document.createElement('a');
        openLink.className = 'proj-btn';
        openLink.href = item?.source || '#';
        openLink.textContent = 'Open';
        actions.appendChild(openLink);

        if (item?.download) {
            const downloadLink = document.createElement('a');
            downloadLink.className = 'proj-btn';
            downloadLink.href = item.download;
            downloadLink.setAttribute('download', item.download);
            downloadLink.textContent = 'Download';
            actions.appendChild(downloadLink);
        }

        card.appendChild(badge);
        card.appendChild(title);
        card.appendChild(preview);
        card.appendChild(actions);
        return card;
    };

    fetch('manifest.json')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            if (!data || !data.evidenceNodes) {
                console.warn('Empty or invalid manifest data');
                return;
            }

            const nodes = Array.isArray(data.evidenceNodes) ? data.evidenceNodes : [];
            const grid = document.getElementById('dynamic-evidence-grid');
            if (grid) {
                grid.replaceChildren(...nodes.map(createSafeEvidenceCard));
            }

            const nodeList = document.getElementById('dynamic-node-list');
            if (nodeList) {
                nodeList.replaceChildren(...nodes.map(createSafeListItem));
            }

            if (data.forensicData) {
                const updateField = (id, value, className = '') => {
                    const el = document.getElementById(id);
                    if (el) {
                        setText(el, value ?? '');
                        if (className) el.className = 'val ' + className;
                    }
                };

                updateField('f-subject', data.forensicData.subject, 'gold');
                updateField('f-theftAmount', data.forensicData.theftAmount, 'red');
                updateField('f-subjects', data.forensicData.subjects, 'red');
                updateField('f-method', data.forensicData.method);
                updateField('f-timestamp', data.forensicData.timestamp, 'green');
                updateField('f-merkleRoot', data.forensicData.merkleRoot, 'green');
            }

            const projection = document.getElementById('dynamic-projection');
            if (projection && data.projectionNodes) {
                const projections = Array.isArray(data.projectionNodes) ? data.projectionNodes : [];
                projection.replaceChildren(...projections.map(createSafeProjectionCard));
            }
        })
        .catch(err => {
            console.error('Error loading manifest:', err);
            const grid = document.getElementById('dynamic-evidence-grid');
            if (grid) {
                grid.textContent = 'Не удалось загрузить данные доказательств.';
            }
        });
});
