module.exports = function(grunt) {

    grunt.loadNpmTasks('grunt-bower-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        bower_concat: {
            all: {
                dest: {
                  'js': 'static/build/_bower.js',
                  'css': 'static/build/_bower.css',
                },
                mainFiles: {
                    'x-editable': ['dist/bootstrap3-editable/js/bootstrap-editable.min.js', 'dist/bootstrap3-editable/css/bootstrap-editable.css'],
                    'jquery-contextmenu': ['src/contextmenu.min.js'],
                    'decouple': ['dist/decouple.min.js'],
                    'slideout.js': ['dist/slideout.min.js', 'index.css'],
                    'jquery-livesearch': ['src/jquery.livesearch.js'],
                    'trumbowyg': ['dist/trumbowyg.min.js', 'dist/ui/trumbowyg.min.css'],
                    'bootstrap-tagsinput': ['dist/bootstrap-tagsinput.min.js', 'dist/bootstrap-tagsinput.css'],
                    'fullpage.js': ['vendors/scrolloverflow.min.js', 'dist/jquery.fullpage.min.js', 'dist/jquery.fullpage.min.css'],
                    'malihu-custom-scrollbar-plugin': ['jquery.mCustomScrollbar.concat.min.js', 'jquery.mCustomScrollbar.css'],
                }, dependencies: {
                    'x-editable': ['jquery', 'bootstrap'],
                    'jquery-livesearch': ['jquery'],
                    'jquery-contextmenu': ['jquery'],
                    'malihu-custom-scrollbar-plugin': ['jquery'],
                    'bootstrap-datetimepicker': ['jquery', 'bootstrap']
                }
            }
        },
        copy: {
            main: {
                files: [
                    {expand: true, src: ['assets/bower/components/trumbowyg/dist/ui/icons.svg'], dest: 'static/build/ui', flatten: true},
                    {expand: true, src: ['assets/bower/components/jQuery-contextMenu/dist/font/**'], dest: 'static/build/font', flatten: true},
                    {expand: true, src: ['assets/bower/components/photoswipe/dist/default-skin/**'], dest: 'static/build', flatten: true},
                    {expand: true, src: ['assets/bower/components/tinymce-dist/themes/modern/**'], dest: 'static/build/themes/modern', flatten: true},
                    {expand: true, src: ['assets/bower/components/tinymce-dist/skins/lightgray/**'], dest: 'static/build/skins/lightgray', flatten: true},
                    {expand: true, src: ['assets/bower/components/tinymce-dist/skins/lightgray/fonts/**'], dest: 'static/build/skins/lightgray/fonts', flatten: true},
                    {expand: true, src: ['assets/bower/components/tinymce-dist/skins/lightgray/img/**'], dest: 'static/build/skins/lightgray/img', flatten: true},
                ],
            },
        }
    });

    // Default task(s).
    grunt.registerTask('default', ['bower_concat', 'copy']);

};