# Maintainer:  Ralf Zerres <ralf.zerres@networkx.de>

pkgname=python-fiovisualizer
_pkgname=fiovisualizer
pkgver=0.r6.g1192828
pkgrel=1
pkgdesc="Data visualisation tool for FIO"
arch=('i686' 'x86_64')
license='Intel'
url="https://01.org/fio-visualizer"
#depends=('python' 'fio=2.1.4' 'python-pyqtgraph')
depends=('python' 'cython' 'fio' 'python-pyqtgraph' 'python-pyqt4')
source=("$_pkgname::git+http://github.com/01org/fiovisualizer.git#branch=master")
#md5sums=('6e2efa185b6b9227dfe16fefd921a8ec')
md5sums=('SKIP')

pkgver() {
  cd "${srcdir}/${_pkgname}"
  if GITTAG="$(git describe --abbrev=0 --tags 2>/dev/null)"; then
    echo "$(sed -e "s/^${_pkgname%%-git}//" -e 's/^[-_/a-zA-Z]\+//' -e 's/[-_+]/./g' <<< ${GITTAG}).r$(git rev-list --count ${GITTAG}..).g$(git log -1 --format="%h")"
  else
    echo "0.r$(git rev-list --count master).g$(git log -1 --format="%h")"
  fi
}

build() {
  echo "Building in (`pwd`)"
  cp ../setup.py "$srcdir/"
  cp ../DESCRIPTION.rst "$srcdir/"
  cp ../__init__.py "$srcdir/$_pkgname/"
  cp ../fio_visualizer.py "$srcdir/$_pkgname/"
}

package() {
  echo "Packaging in (`pwd`)"
  cd "$srcdir"
  python setup.py install --prefix=/usr --root="$pkgdir" --optimize 1
}

