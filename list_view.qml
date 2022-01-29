ListView {
    id: songListView
    model: yourSongModel
    delegate: RowLayout {
        width: songListView.width
        height: 50
        Image {
            source: model.image
        }
        ColumnLayout {
            Label {
                Layout.fillWidth: true
                text: model.title
            }
            Label {
                Layout.fillWidth: true
                text: model.album
            }
        }
        Label {
            text: model.length
        }
    }
}