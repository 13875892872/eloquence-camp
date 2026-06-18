/** 按角色过滤侧边栏菜单 */
export function filterMenusByRole(menus, role = 'super_admin') {
  return menus
    .map((item) => {
      if (item.roles && !item.roles.includes(role)) return null
      if (item.type === 'sub' && item.children) {
        const children = item.children.filter(
          (c) => !c.roles || c.roles.includes(role)
        )
        if (!children.length) return null
        return { ...item, children }
      }
      return item
    })
    .filter(Boolean)
}
