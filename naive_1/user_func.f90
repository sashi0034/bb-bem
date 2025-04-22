module user_func
  integer, parameter :: KIND_REAL = kind(1d0) ! 実数変数のKIND
  real(kind = KIND_REAL), parameter :: PI = 3.141592653589793 ! 円周率
  real(kind = KIND_REAL), parameter :: EPSILON_0 = 8.854187818 * 1d-12 ! 真空の透磁率

  type :: coordinate
     real(8) :: x ,y ,z
  end type coordinate

  public face_integral

  contains

  !****************************************************************************
  !
  !  三角形から点 P への寄与の積分計算 （技術報告4章を参考）
  !
  !****************************************************************************
  real(kind = KIND_REAL) function face_integral(xs, ys, zs, x, y, z)
    real(kind = KIND_REAL), intent(in) :: xs(3), ys(3), zs(3) ! 三角形の頂点の座標
    real(kind = KIND_REAL), intent(in) :: x, y, z ! 点 P の座標

      real(kind = KIND_REAL) :: r(3) ! 点Pと3頂点の距離
      real(kind = KIND_REAL) :: xi, xj, yi, dx, dy, t, l, m, d, ti, tj
      real(kind = KIND_REAL) :: theta, omega, q, g, zp, zpabs

      integer :: i, j
      real(kind = KIND_REAL) :: u(3), v(3), w(3) ! ※これらのベクトルの添字は x, y, z成分を表す
      real(kind = KIND_REAL) :: ox, oy, oz ! 原点座標

      r(:) = sqrt( (xs(:) - x)**2 + (ys(:) - y)**2 + (zs(:) - z)**2 )

      ! 面の法線ベクトルを外積で求める
      u(1) = xs(2) - xs(1);  v(1) = xs(3) - xs(2)
      u(2) = ys(2) - ys(1);  v(2) = ys(3) - ys(2)
      u(3) = zs(2) - zs(1);  v(3) = zs(3) - zs(2)
      call cross_product(u, v, w)
      w(:) = w(:) / sqrt( dot_product(w, w) )

      ! 原点とzpを求める（ O = P - zp * w として直交条件から）
      u(1) = x - xs(1);  u(2) = y - ys(1);  u(3) = z - zs(1)
      zp = dot_product(u, w)
      ox = x - zp * w(1);  oy = y - zp * w(2);  oz = z - zp * w(3)
      zpabs = abs(zp)

      face_integral = 0d0
      do i = 1, 3
         j = mod(i, 3) + 1
         u(1) = xs(j) - ox;  u(2) = ys(j) - oy; u(3) = zs(j) - oz; ! j の位置ベクトル
         ! 点 j を（座標変換後の）x 軸上にとる（yj = 0）
         xj = sqrt( dot_product(u, u) )
         u(:) = u(:) / xj ! （座標変換後の）x方向基底ベクトル
         call cross_product(w, u, v) ! （座標変換後の）y方向基底ベクトル
         xi = (xs(i) - ox) * u(1) + (ys(i) - oy) * u(2) + (zs(i) - oz) * u(3)
         yi = (xs(i) - ox) * v(1) + (ys(i) - oy) * v(2) + (zs(i) - oz) * v(3)

         dx = xj - xi;  dy = - yi ! (yj = 0)
         t = sqrt( dx**2 + dy**2 )
         l = dx/t;  m = dy/t
         d = l * yi - m * xi
         ti = l * xi + m * yi;  tj = l * xj ! (yj = 0)

         !            theta = sign(1d0, yi) * acos( xi / sqrt( xi**2 + yi**2 ) ) ! (xj > 0, yj = 0)
         theta = atan2(yi, xi) ! （資料と少し違う方法）
         omega = theta - atan2( r(i) * d, zpabs * ti ) + atan2( r(j) * d, zpabs * tj )
         q = log( (r(j) + tj) / ( r(i) + ti ) )
         g = d * q - zpabs * omega
         face_integral = face_integral + g
      enddo

      face_integral = abs(face_integral) / (4d0 * PI * EPSILON_0)

    end function

    !****************************************************************************
    !
    !  3次元外積計算 w = u × v
    !
    !****************************************************************************
    subroutine cross_product(u, v, w)
      real(kind = KIND_REAL) :: u(3), v(3), w(3)

      w(1) = u(2) * v(3) - u(3) * v(2)
      w(2) = u(3) * v(1) - u(1) * v(3)
      w(3) = u(1) * v(2) - u(2) * v(1)

    end subroutine cross_product

  end module user_func

!****************************************************************************
!
!   C からの呼び出しを想定したユーザ関数の例
!   C から呼ぶときの名前は 一行目の name = '' で指定
!
!   返り値は 行列の（i, j）要素
!
!****************************************************************************
  real(8) function element_ij(i, j, nond, nofc, np, face2node)
  use user_func
  integer ,intent(in) :: i, j, nond, nofc ! これらは値渡し
  type(coordinate), intent(in) :: np(*)
  integer, intent(in) :: face2node(3, *)

  integer :: n(3) ! 面を構成する 3 節点
  real(8) :: xf(3), yf(3), zf(3) ! 3 節点の座標
  real(8) :: xp, yp, zp ! 考察点の座標

!  i = ii + 1 ! 値渡しにしているので変えてよい
!  j = jj + 1

  ! 面 i について
  n(1:3) = face2node(1:3, i+1) + 1
  xf(1:3) = np( n(1:3) )%x
  yf(1:3) = np( n(1:3) )%y
  zf(1:3) = np( n(1:3) )%z
  ! 面 i の重心
  xp = sum( xf(1:3) ) / 3d0
  yp = sum( yf(1:3) ) / 3d0
  zp = sum( zf(1:3) ) / 3d0

  ! 面 j について
  n(1:3) = face2node(1:3, j+1) + 1
  xf(1:3) = np( n(1:3) )%x
  yf(1:3) = np( n(1:3) )%y
  zf(1:3) = np( n(1:3) )%z

  element_ij = face_integral(xf, yf, zf, xp, yp, zp)

end function element_ij
