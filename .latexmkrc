$out_dir="out";
# PDF 及 .aux 等中间文件主名（XeLaTeX）；与 thesis 中文题名一致便于归档
$jobname = '基于机器学习的固态硬盘故障预测与寿命提升方法研究';
$pdf_mode=5;
$xelatex="xelatex -synctex=1";
$xdvipdfmx="xdvipdfmx -q -E -o %D %O %S";
$clean_ext = 'thm bbl hd loe xdv run.xml nlg nls';
$makeindex = 'makeindex -s gind.ist %O -o %D %S';

# Custom dependency and function for nomencl package 
add_cus_dep( 'nlo', 'nls', 0, 'makenlo2nls' );
sub makenlo2nls {
 system("makeindex \"$_[0].nlo\" -s nomencl.ist -o \"$_[0].nls\" -t \"$_[0].nlg\"" );
}


@default_files=('zjuthesis.tex')
