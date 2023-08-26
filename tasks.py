from invoke import task
from os import environ,  chdir, path, makedirs
from sys import exit
from vxbase import fromenv, version


def coverage_func (c, html=''):
    cover_dir = environ.get('CI_COMMIT_REF_SLUG', 'coverage')
    if not path.exists(cover_dir):
        makedirs(cover_dir)
    c.run('go test -covermode=count -coverprofile={}/coverage.cov ./...'.format(cover_dir))
    c.run('go tool cover -func={}/coverage.cov'.format(cover_dir))
    c.run('gocover-cobertura < {d}/coverage.cov > {d}/coverage.xml'.format(d=cover_dir))
    if html == 'html':
        c.run('go tool cover -html={d}/coverage.cov -o {d}/index.html'.format(d=cover_dir))
    c.run('rm -rf {}/*.cov'.format(cover_dir))


@task
def dep(c):
    c.run('go get ./...')


@task
def lint(c):
    c.run(r'golangci-lint run ./... --timeout=5m0s  -e "Error return value of .(rClient\.)"')


@task
def test(c):
    coverage_func(c, 'html')


@task
def race(c):
    c.run('go test -race -short ./...')


@task
def cyclo(c):
    c.run(r'gocyclo -over 10 .')


@task
def sec(c):
    c.run(r"gosec -exclude-dir 'examples/*' ./...")


@task
def fmt(c):
    fmts = c.run(r'gofmt -l .')
    if fmts.stdout != "":
        print("\nThe code have format issues (see the list above this output), please run  'gofmt -d .' to list the issues")
        print("Please execute 'invoke fmt -e' before pushing")
        exit(1)

    imps = c.run(r'goimports -l .')
    if imps.stdout != "":
        print("\nFailed the imports check (see the list above this output), use 'goimports -d .' to check the diff")
        print("Please execute 'invoke fmt -e' before pushing")
        exit(1)


@task
def release(c):
    if not fromenv.is_ci():
        v = version.get_version(".bumpversion.cfg")
        if v == '':
            print("Failed read the version from .bumpversion.cfg")
            exit(1)
        c.run('git push vx master')
        c.run('git push vx v' + v)


