def main():
    from pkg_resources import resource_filename, Requirement
    import os
    cwd = os.path.realpath('.')
    os.environ['FLASKPATH'] = cwd
    from fabric.main import main
    filename = resource_filename(Requirement.parse("filament"), "filament/fabfile")
    main([filename])



