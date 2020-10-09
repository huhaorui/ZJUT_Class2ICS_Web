class Table {
    constructor(id, col) {
        this.id = id
        this.col = col
    }

    removeAll() {
        $(`#${this.id} tr:not(:first)`).remove();
        mdui.updateTables()
    }

    addAll(items) {
        items.forEach((item) => {
            console.log(item)
            let tr = document.createElement('tr')
            for (let key in item) {
                let value = item[key]
                let td = document.createElement('td')
                if (key === 'code' && value !== 'null') {
                    td.style.color = value
                    value = '████████'
                }
                td.innerHTML = value
                tr.appendChild(td)
            }
            $(`#${this.id}`).append(tr)
        })

        mdui.updateTables()
    }

    filter_color(data, colors) {
        let items = data.filter((item) =>
            (colors.red && item.code === 'red')
            || (colors.yellow && item.code === 'yellow')
            || (colors.green && item.code === 'green')
            || (colors.lightgray && item.code === 'lightgray')
            || (colors.aquamarine && item.code === 'aquamarine')
            || (colors.wheat && item.code === 'wheat')
        )
        this.removeAll()
        this.addAll(items)
    }
}