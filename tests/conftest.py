from pathlib import Path
import os
import shutil
import subprocess
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))


@pytest.fixture
def make_link(monkeypatch):
    """Create a real symlink, or an unprivileged Windows directory junction.

    For a file target on Windows, return a path through a junction to its parent.
    This still exercises rejection of link traversal without requiring Developer Mode.
    """
    synthetic=set();created=[]
    original_symlink=Path.is_symlink
    original_junction=getattr(Path,'is_junction',lambda _self:False)
    monkeypatch.setattr(Path,'is_symlink',lambda self:self.absolute() in synthetic or original_symlink(self))
    monkeypatch.setattr(Path,'is_junction',lambda self:self.absolute() in synthetic or original_junction(self),raising=False)
    def create(link, target, *, target_is_directory=False):
        link=Path(link);target=Path(target)
        if os.name!='nt':
            link.symlink_to(target,target_is_directory=target_is_directory)
            create.actual[str(link)]=True
            return link
        if target_is_directory:
            junction_target=target
        else:
            junction_target=link.parent/(link.name+'-junction-target')
            junction_target.mkdir()
            shutil.copyfile(target,junction_target/target.name)
        result=subprocess.run(['cmd','/d','/c','mklink','/J',str(link),str(junction_target)],
                              capture_output=True,text=True)
        actual=result.returncode==0
        if not actual:
            if os.environ.get('CMBA_REQUIRE_REAL_LINK')=='1':
                pytest.fail('real Windows junction required for target-platform qualification: '+result.stderr)
            # Some restricted Windows runners deny reparse-point creation. Preserve
            # branch coverage with a narrowly scoped synthetic junction marker; an
            # unrestricted target-platform replay must still exercise the real path.
            link.mkdir()
            if not target_is_directory:shutil.copyfile(target,link/target.name)
            synthetic.add(link.absolute())
        else:created.append(link)
        returned=link if target_is_directory else link/target.name
        create.actual[str(returned)]=actual
        return returned
    create.actual={}
    create.is_actual=lambda path:create.actual.get(str(path),False)
    yield create
    for link in reversed(created):
        if link.exists():os.rmdir(link)
